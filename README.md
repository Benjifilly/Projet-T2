# 🏋️‍♂️ Projet de Terminale Générale - BDD Réservation de Salles de Musculation

## 📖 Description
Ce projet est réalisé dans le cadre de la terminale générale. Il s'agit d'une application web permettant de gérer la réservation de salles de musculation. Elle inclut des fonctionnalités comme l'inscription, la connexion, et la gestion des réservations.

## 🛠️ Technologies Utilisées
- Python (Flask)
- SQLite pour la base de données
- HTML/CSS/JavaScript pour l'interface utilisateur

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

3. **Installer les librairies requises :**
Assurez-vous d'avoir Python installé sur votre machine, puis installez les dépendances avec `pip`.
```bash
pip install flask werkzeug
```

4. **Exécuter le script Python :**
Pour démarrer l'application en local, exécutez le fichier Python principal :
```bash
python incription.py
```

5. **Ouvrir l'application dans le navigateur :**
L'application sera accessible à l'adresse suivante dans votre navigateur :
```
http://localhost:5000
```

## 📚 Librairies Principales Utilisées
Le projet utilise les librairies Python suivantes :
- `Flask` : Pour gérer l'application web.
- `Werkzeug` : Pour la gestion des mots de passe et des sessions utilisateur.
- `sqlite3` : Pour gérer la base de données locale.

```python
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify   
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import os
```

## ⚠️ Base de Données
**Important :** La base de données SQLite incluse dans le projet **n'est pas vide** et contient déjà des informations. Il est recommandé de vérifier ou réinitialiser la base de données avant de l'utiliser en production.

## 👤 Auteur
- **Filly Benjamin**
- Terminale Générale, Projet 2024/2025

---
💡 **Merci d'avoir consulté ce projet !** Si vous avez des questions ou des suggestions, n'hésitez pas à ouvrir une issue sur GitHub.

