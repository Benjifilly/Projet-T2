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
            flash('Veuillez vous connecter pour accéder à cette page')
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


@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return "Bienvenue sur votre tableau de bord"  # À développer selon les besoins

if __name__ == '__main__':
    app.run(debug=True)
