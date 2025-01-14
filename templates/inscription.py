from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici' 

DATABASE = 'Sallemuscu.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('inscription.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Utilisateur WHERE "E-mail" = ?', (email,))
        if cursor.fetchone():
            flash('Cet email est déjà utilisé')
            return redirect(url_for('index'))

        cursor.execute('SELECT * FROM Utilisateur WHERE Telephone = ?', (telephone,))
        if cursor.fetchone():
            flash('Ce numéro de téléphone est déjà utilisé')
            return redirect(url_for('index'))

        cursor.execute('''
            INSERT INTO Utilisateur (Nom, Prénom, "E-mail", Telephone)
            VALUES (?, ?, ?, ?)
        ''', (nom, prenom, email, telephone))
        
        conn.commit()
        flash('Compte créé avec succès!')
        return redirect(url_for('index'))

    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        flash('Une erreur est survenue lors de la création du compte')
        return redirect(url_for('index'))
    
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)