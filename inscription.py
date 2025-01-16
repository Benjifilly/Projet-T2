from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'

DATABASE = 'D:\Projet-T2-main\Sallemuscu.db'

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

if __name__ == '__main__':
    app.run(debug=True)
