import sqlite3

def init_db():
    conn = sqlite3.connect("Sallemuscu.db")
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Creneau (
            ID_creneau INTEGER PRIMARY KEY UNIQUE,
            Heure_debut TEXT,
            Heure_fin TEXT,
            ID_salle TEXT
        ) STRICT;

        CREATE TABLE IF NOT EXISTS Equipement (
            ID_equipement INTEGER PRIMARY KEY UNIQUE,
            Nom TEXT,
            Description TEXT,
            Type TEXT,
            Disponibilite TEXT,
            URL TEXT
        );

        CREATE TABLE IF NOT EXISTS Liste_attente (
            ID_attente INTEGER PRIMARY KEY UNIQUE,
            Date_demande TEXT,
            Position INTEGER UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Utilisateur (
            ID_utilisateur INTEGER PRIMARY KEY UNIQUE,
            Nom TEXT,
            Prénom TEXT,
            "E-mail" TEXT UNIQUE,
            Telephone INTEGER UNIQUE,
            Mot_de_passe TEXT
        );

        CREATE TABLE IF NOT EXISTS Reservation (
            ID_reservation INTEGER PRIMARY KEY UNIQUE,
            ID_utilisateur INTEGER REFERENCES Utilisateur(ID_utilisateur),
            ID_creneau INTEGER REFERENCES Creneau(ID_creneau),
            Date_reservation TEXT,
            Statut TEXT
        );
    ''')

    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    init_db()