from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify   
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import os


app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'

DATABASE = 'Projet-T2-main\Sallemuscu.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('inscription.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM Utilisateur WHERE "E-mail" = ?', (email,))
                user = cursor.fetchone()

                if user and check_password_hash(user['Mot_de_passe'], password):
                    session['user_id'] = user['ID_utilisateur']
                    session['user_name'] = user['Prénom']
                    flash('Connexion réussie!')
                    return redirect(url_for('dashboard'))
                flash('Email ou mot de passe incorrect', 'error')
                return redirect(url_for('index'))
        except sqlite3.Error as e:
            flash('Erreur lors de la connexion à la base de données', 'error')
            print(f"Erreur SQLite: {e}")
            return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    password = request.form['password']
    confirm_password = request.form['confirm-password']

    if password != confirm_password:
        flash('Les mots de passe ne correspondent pas', 'error')
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM Utilisateur WHERE "E-mail" = ?', (email,))
            if cursor.fetchone():
                flash('Cet email est déjà utilisé', 'error')
                return redirect(url_for('index'))

            cursor.execute('SELECT * FROM Utilisateur WHERE Telephone = ?', (telephone,))
            if cursor.fetchone():
                flash('Ce numéro de téléphone est déjà utilisé', 'error')
                return redirect(url_for('index'))

            cursor.execute('''
                INSERT INTO Utilisateur (Nom, Prénom, "E-mail", Telephone, Mot_de_passe)
                VALUES (?, ?, ?, ?, ?)
            ''', (nom, prenom, email, telephone, hashed_password))
            conn.commit()

            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter', 'success')
            return redirect(url_for('index'))

    except sqlite3.Error as e:
        flash('Une erreur est survenue lors de la création du compte', 'error')
        print(f"Erreur SQLite: {e}")
        return redirect(url_for('index'))
    
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Si méthode GET, on récupère les informations de l'utilisateur
            if request.method == 'GET':
                cursor.execute('SELECT Nom, Prénom, "E-mail", Telephone FROM Utilisateur WHERE ID_utilisateur = ?', (user_id,))
                user = cursor.fetchone()
                if user:
                    return render_template('profile.html', user=user)
                flash('Utilisateur introuvable', 'error')
                return redirect(url_for('dashboard'))

            # Si méthode POST, on met à jour les informations
            if request.method == 'POST':
                nom = request.form['nom']
                prenom = request.form['prenom']
                email = request.form['email']
                telephone = request.form['telephone']

                # Validation des champs
                if not nom or not prenom or not email or not telephone:
                    flash('Tous les champs sont requis', 'error')
                    return redirect(url_for('profile'))

                # Vérification des doublons pour l'email et le téléphone
                cursor.execute('SELECT ID_utilisateur FROM Utilisateur WHERE "E-mail" = ? AND ID_utilisateur != ?', (email, user_id))
                if cursor.fetchone():
                    flash('Cet email est déjà utilisé', 'error')
                    return redirect(url_for('profile'))

                cursor.execute('SELECT ID_utilisateur FROM Utilisateur WHERE Telephone = ? AND ID_utilisateur != ?', (telephone, user_id))
                if cursor.fetchone():
                    flash('Ce numéro de téléphone est déjà utilisé', 'error')
                    return redirect(url_for('profile'))

                # Mise à jour des informations
                cursor.execute('''
                    UPDATE Utilisateur
                    SET Nom = ?, Prénom = ?, "E-mail" = ?, Telephone = ?
                    WHERE ID_utilisateur = ?
                ''', (nom, prenom, email, telephone, user_id))
                conn.commit()

                flash('Profil mis à jour avec succès', 'success')
                return redirect(url_for('profile'))

    except sqlite3.Error as e:
        flash('Erreur lors de la mise à jour du profil', 'error')
        print(f"Erreur SQLite: {e}")
        return redirect(url_for('dashboard'))
    
@app.route('/reserve_slot', methods=['POST'])
@login_required
def reserve_slot():
    room = request.form.get('room')
    start_time = request.form.get('time')
    duration = int(request.form.get('duration'))
    user_id = session['user_id']  # Identifiant de l'utilisateur connecté

    if not room or not start_time or not duration:
        flash('Tous les champs sont requis.', 'error')
        return redirect(url_for('reservation'))

    # Calcul de l'heure de fin
    start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
    end_time_dt = start_time_dt + timedelta(minutes=duration)
    end_time = end_time_dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Vérifiez si le créneau est disponible
            cursor.execute('''
                SELECT * FROM Creneau
                WHERE (Heure_debut < ? AND Heure_fin > ?) AND ID_salle = ?
            ''', (end_time, start_time, room))
            existing_creneau = cursor.fetchone()

            if existing_creneau:
                # Ajouter en liste d'attente si le créneau est déjà pris
                cursor.execute('''
                    INSERT INTO Liste_attente (Date_demande, Position)
                    VALUES (?, (SELECT COALESCE(MAX(Position), 0) + 1 FROM Liste_attente))
                ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
                conn.commit()
                flash('Le créneau est déjà réservé. Vous avez été ajouté à la liste d’attente.', 'error')
                return redirect(url_for('reservation'))

            # Sinon, ajouter une réservation
            cursor.execute('''
                INSERT INTO Creneau (Heure_debut, Heure_fin, ID_salle)
                VALUES (?, ?, ?)
            ''', (start_time, end_time, room))
            creneau_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO Reservation (ID_creneau, Date_reservation, Statut, ID_utilisateur)
                VALUES (?, ?, ?, ?)
            ''', (creneau_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Confirmée", user_id))
            conn.commit()

            flash('Réservation effectuée avec succès !', 'success')
            return redirect(url_for('reservation'))

    except sqlite3.Error as e:
        flash('Une erreur est survenue lors de la réservation.', 'error')
        print(f"Erreur SQLite: {e}")
        return redirect(url_for('reservation'))
    
@app.route('/reservation')
@login_required
def reservation():
    if request.args.get('format') == 'json':
        # Retourne les données des réservations
        user_id = session['user_id']
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT Creneau.Heure_debut, Creneau.Heure_fin, Reservation.Statut, Reservation.ID_creneau,
                           CASE WHEN Reservation.ID_utilisateur = ? THEN 1 ELSE 0 END AS is_user
                    FROM Creneau
                    JOIN Reservation ON Creneau.ID_creneau = Reservation.ID_creneau
                ''', (user_id,))
                reservations = cursor.fetchall()

                events = [
                    {
                        'title': "Ma réservation" if r['is_user'] else "Réservé",
                        'start': r['Heure_debut'],
                        'end': r['Heure_fin'],
                        'backgroundColor': '#28a745' if r['is_user'] else '#dc3545',
                        'borderColor': '#28a745' if r['is_user'] else '#dc3545',
                        'textColor': '#fff'
                    } for r in reservations
                ]
                return jsonify(events)

        except sqlite3.Error as e:
            print(f"Erreur SQLite: {e}")
            return jsonify([]), 500
    else:
        return render_template('reservation.html')


@app.route('/api/reservations')
@login_required
def api_reservations():
    user_id = session['user_id']
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Creneau.Heure_debut, Creneau.Heure_fin, Reservation.Statut, Reservation.ID_creneau,
                       CASE WHEN Reservation.ID_utilisateur = ? THEN 1 ELSE 0 END AS is_user
                FROM Creneau
                JOIN Reservation ON Creneau.ID_creneau = Reservation.ID_creneau
            ''', (user_id,))
            reservations = cursor.fetchall()

            events = [
                {
                    'title': "Ma réservation" if r['is_user'] else "Réservé",
                    'start': r['Heure_debut'],
                    'end': r['Heure_fin'],
                    'backgroundColor': '#28a745' if r['is_user'] else '#dc3545',
                    'borderColor': '#28a745' if r['is_user'] else '#dc3545',
                    'textColor': '#fff'
                } for r in reservations
            ]
            return jsonify(events)

    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        return jsonify([]), 500
    
@app.route('/my_reservations')
@login_required
def my_reservations():
    user_id = session['user_id']
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Reservation.ID_reservation AS id, 
                       Creneau.ID_creneau AS room, 
                       Creneau.Heure_debut AS start_time, 
                       Creneau.Heure_fin AS end_time, 
                       Reservation.Statut AS status
                FROM Reservation
                JOIN Creneau ON Reservation.ID_creneau = Creneau.ID_creneau
                WHERE Reservation.ID_utilisateur = ?
            ''', (user_id,))
            reservations = cursor.fetchall()

        return render_template('my_reservations.html', reservations=reservations)

    except sqlite3.Error as e:
        flash('Erreur lors du chargement des réservations.', 'error')
        print(f"Erreur SQLite: {e}")
        return render_template('my_reservations.html', reservations=[])
    
@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Vérifiez que la réservation appartient à l'utilisateur connecté
            cursor.execute('''
                SELECT * FROM Reservation WHERE ID_reservation = ? AND ID_utilisateur = ?
            ''', (reservation_id, session['user_id']))
            reservation = cursor.fetchone()

            if not reservation:
                flash('Réservation introuvable ou vous n\'êtes pas autorisé à l\'annuler.', 'error')
                return redirect(url_for('my_reservations'))

            # Supprimez la réservation
            cursor.execute('DELETE FROM Reservation WHERE ID_reservation = ?', (reservation_id,))
            conn.commit()
            flash('Réservation annulée avec succès.', 'success')
            return redirect(url_for('my_reservations'))
    except sqlite3.Error as e:
        flash('Erreur lors de l\'annulation de la réservation.', 'error')
        print(f"Erreur SQLite: {e}")
        return redirect(url_for('my_reservations'))

    
def calculate_end_time(start_time):
    start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
    end_dt = start_dt + timedelta(hours=1) 
    return end_dt.strftime("%Y-%m-%d %H:%M:%S")

    
@app.route('/modify_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def modify_reservation(reservation_id):
    new_date = request.form.get('new_date')

    if not new_date:
        flash('Une nouvelle date est requise.', 'error')
        return redirect(url_for('my_reservations'))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Vérifiez que la réservation appartient à l'utilisateur connecté
            cursor.execute('''
                SELECT * FROM Reservation WHERE ID_reservation = ? AND ID_utilisateur = ?
            ''', (reservation_id, session['user_id']))
            reservation = cursor.fetchone()

            if not reservation:
                flash('Réservation introuvable ou vous n\'êtes pas autorisé à la modifier.', 'error')
                return redirect(url_for('my_reservations'))

            # Mettez à jour la réservation avec la nouvelle date
            cursor.execute('''
                UPDATE Creneau
                SET Heure_debut = ?, Heure_fin = ?
                WHERE ID_creneau = (
                    SELECT ID_creneau FROM Reservation WHERE ID_reservation = ?
                )
            ''', (new_date, calculate_end_time(new_date), reservation_id))
            conn.commit()
            flash('Réservation modifiée avec succès.', 'success')
            return redirect(url_for('my_reservations'))
    except sqlite3.Error as e:
        flash('Erreur lors de la modification de la réservation.', 'error')
        print(f"Erreur SQLite: {e}")
        return redirect(url_for('my_reservations'))
    
@app.route('/equipements')
def equipements():
    connection = sqlite3.connect('D:\Projet-T2-main\Sallemuscu.db')
    cursor = connection.cursor()
    cursor.execute("SELECT Nom, Description, Type, Disponibilite, URL FROM Equipement")
    equipements = cursor.fetchall()
    connection.close()

    return render_template('equipements.html', equipements=equipements)

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = session['user_id']
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Utilisateur WHERE ID_utilisateur = ?', (user_id,))
            conn.commit()
            flash('Votre compte a été supprimé avec succès.', 'success')
    except sqlite3.Error as e:
        flash('Une erreur est survenue lors de la suppression de votre compte.', 'error')
        print(f"Erreur SQLite: {e}")
        return redirect(url_for('profile'))
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_name=session.get('user_name'))

@app.route('/reservation')
@login_required
def reservation_page():
    return render_template('reservation.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)
