# 🏋s️ Projet de Terminale Générale - BDD Réservation de Salles de Musculation

## 📚 Description
Ce projet est réalisé dans le cadre de la terminale générale. Il s'agit d'une application web permettant de gérer la réservation de salles de musculation. Elle inclut des fonctionnalités comme l'inscription, la connexion, la gestion des réservations et une liste d'attente automatisée.

## 🛠️ Technologies Utilisées
- **Backend :** Python (Flask)
- **Base de données :** SQLite
- **Frontend :** HTML, CSS, JavaScript
- **Librairies frontend :** FullCalendar.js pour la gestion des réservations
- **Authentification & Sécurité :** Werkzeug (hashing des mots de passe)

## 🚀 Installation en Local
Pour exécuter ce projet localement, suivez les étapes ci-dessous :

1. **Cloner le dépôt GitHub :**
```bash
git clone https://github.com/Benjifilly/Projet-T2
```

2. **Accéder au répertoire du projet :**
```bash
cd Projet-T2
```

3. **Configurer un environnement virtuel (recommandé) :**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

4. **Installer les dépendances requises :**
Assurez-vous d'avoir Python installé sur votre machine, puis exécutez :
```bash
pip install -r requirements.txt
```

5. **Démarrer l'application Flask :**
```bash
python inscription.py
```

6. **Ouvrir l'application dans le navigateur :**
L'application sera accessible à l'adresse suivante :
[http://localhost:5000](http://localhost:5000)

## 📚 Librairies Principales Utilisées
Le projet repose sur les librairies suivantes :
- **Flask** : Framework web principal
- **Werkzeug** : Gestion des mots de passe et sécurité
- **SQLite3** : Base de données locale
- **FullCalendar.js** : Interface calendrier pour les réservations
- **Flask-Session** : Gestion des sessions utilisateurs

## ⚠️ Base de Données
**Important :** La base de données SQLite incluse contient déjà des informations de test. Il est recommandé de la réinitialiser avant une utilisation en production.

Pour réinitialiser la base de données :
```bash
rm Sallemuscu.db  # Sur Windows : del Sallemuscu.db
python init_db.py  # Réinitialisation de la base
```

## 👤 Auteur
- **Filly Benjamin**
- Terminale Générale, Projet 2024/2025

---
💡 **Merci d'avoir consulté ce projet !** Si vous avez des questions ou suggestions, ouvrez une issue sur GitHub.

