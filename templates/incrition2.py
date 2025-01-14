import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from ttkthemes import ThemedTk

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Réservation")
        
        # Mise en plein écran
        self.root.state('zoomed')
        
        # Configuration du style
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12))
        
        # Frame principal qui contiendra toutes les pages
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialisation des pages
        self.pages = {}
        self.current_page = None
        
        # Création des pages
        self.create_home_page()
        self.create_inscription_page()
        self.create_login_page()
        
        # Afficher la page d'accueil
        self.show_page('home')

    def create_home_page(self):
        home_frame = ttk.Frame(self.main_container)
        
        # Conteneur centré
        center_frame = ttk.Frame(home_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titre
        title = ttk.Label(center_frame, text="Système de Réservation", 
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=20)
        
        # Boutons
        ttk.Button(center_frame, text="S'inscrire", 
                  command=lambda: self.show_page('inscription'),
                  width=30).pack(pady=10)
        
        ttk.Button(center_frame, text="Se connecter", 
                  command=lambda: self.show_page('login'),
                  width=30).pack(pady=10)
        
        self.pages['home'] = home_frame

    def create_inscription_page(self):
        inscription_frame = ttk.Frame(self.main_container)
        
        # Conteneur centré
        center_frame = ttk.Frame(inscription_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titre
        title = ttk.Label(center_frame, text="Création de compte", 
                         font=('Helvetica', 24, 'bold'))
        title.pack(pady=20)
        
        # Variables
        self.nom_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.telephone_var = tk.StringVar()
        
        # Champs
        self.create_entry_field(center_frame, "Nom :", self.nom_var)
        self.create_entry_field(center_frame, "Prénom :", self.prenom_var)
        self.create_entry_field(center_frame, "Email :", self.email_var)
        self.create_entry_field(center_frame, "Téléphone :", self.telephone_var)
        
        # Boutons
        ttk.Button(center_frame, text="S'inscrire", 
                  command=self.inscrire, width=30).pack(pady=20)
        
        ttk.Button(center_frame, text="Retour", 
                  command=lambda: self.show_page('home'),
                  width=30).pack(pady=10)
        
        # Message d'état
        self.message_label = ttk.Label(center_frame, text="", font=('Helvetica', 10))
        self.message_label.pack(pady=10)
        
        self.pages['inscription'] = inscription_frame

    def create_login_page(self):
        login_frame = ttk.Frame(self.main_container)
        
        # Frame de recherche en haut
        search_frame = ttk.Frame(login_frame)
        search_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Barre de recherche
        ttk.Label(search_frame, text="Rechercher un utilisateur :",
                 font=('Helvetica', 14)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_users)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                               font=('Helvetica', 12), width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Frame pour la liste des utilisateurs
        list_frame = ttk.Frame(login_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview pour afficher les utilisateurs
        columns = ('ID', 'Nom', 'Prénom', 'Email', 'Téléphone')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement de la liste et scrollbar
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton de connexion et retour
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text="Se connecter", 
                  command=self.login_selected_user,
                  width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Retour", 
                  command=lambda: self.show_page('home'),
                  width=30).pack(side=tk.RIGHT, padx=5)
        
        self.pages['login'] = login_frame

    def create_entry_field(self, parent, label_text, variable):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)
        ttk.Entry(frame, textvariable=variable, width=30).pack(side=tk.LEFT, padx=5)

    def show_page(self, page_name):
        if self.current_page:
            self.pages[self.current_page].pack_forget()
        
        self.pages[page_name].pack(fill=tk.BOTH, expand=True)
        self.current_page = page_name
        
        # Si c'est la page de login, mettre à jour la liste des utilisateurs
        if page_name == 'login':
            self.update_users_list()

    def filter_users(self, *args):
        search_term = self.search_var.get().lower()
        self.update_users_list(search_term)

    def update_users_list(self, search_term=''):
        # Effacer la liste actuelle
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        try:
            conn = sqlite3.connect('Sallemuscu.db')
            cursor = conn.cursor()
            
            # Requête avec filtre si un terme de recherche est fourni
            query = '''
                SELECT * FROM Utilisateur 
                WHERE lower(Nom) LIKE ? 
                OR lower(Prénom) LIKE ? 
                OR lower("E-mail") LIKE ?
            '''
            search_pattern = f'%{search_term}%'
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            
            # Ajouter les utilisateurs filtrés à la liste
            for row in cursor.fetchall():
                self.users_tree.insert('', 'end', values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur de base de données : {str(e)}")
            
        finally:
            conn.close()

    def login_selected_user(self):
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un utilisateur")
            return
            
        user_data = self.users_tree.item(selected_item[0])['values']
        # Ici, vous pouvez ajouter la logique pour gérer la connexion
        messagebox.showinfo("Connexion", 
                          f"Connecté en tant que {user_data[1]} {user_data[2]}")
        # À l'avenir, vous pourrez rediriger vers la page de réservation

    def inscrire(self):
        # Récupération et validation des données
        nom = self.nom_var.get().strip()
        prenom = self.prenom_var.get().strip()
        email = self.email_var.get().strip()
        telephone = self.telephone_var.get().strip()
        
        # Validations
        if not all([nom, prenom, email, telephone]):
            self.show_message("Tous les champs sont obligatoires", True)
            return
            
        if not self.validate_email(email):
            self.show_message("Format d'email invalide", True)
            return
            
        if not self.validate_telephone(telephone):
            self.show_message("Le téléphone doit contenir 10 chiffres", True)
            return
            
        try:
            conn = sqlite3.connect('Sallemuscu.db')
            cursor = conn.cursor()
            
            # Vérification des doublons
            cursor.execute('SELECT * FROM Utilisateur WHERE "E-mail" = ?', (email,))
            if cursor.fetchone():
                self.show_message("Cet email est déjà utilisé", True)
                return
                
            cursor.execute('SELECT * FROM Utilisateur WHERE Telephone = ?', (telephone,))
            if cursor.fetchone():
                self.show_message("Ce numéro de téléphone est déjà utilisé", True)
                return
            
            # Insertion
            cursor.execute('''
                INSERT INTO Utilisateur (Nom, Prénom, "E-mail", Telephone)
                VALUES (?, ?, ?, ?)
            ''', (nom, prenom, email, telephone))
            
            conn.commit()
            self.show_message("Compte créé avec succès!")
            
            # Réinitialisation des champs
            for var in [self.nom_var, self.prenom_var, self.email_var, self.telephone_var]:
                var.set("")
                
        except sqlite3.Error as e:
            self.show_message(f"Erreur lors de l'inscription: {str(e)}", True)
            
        finally:
            conn.close()

    def show_message(self, message, is_error=False):
        self.message_label.config(text=message, 
                                foreground='red' if is_error else 'green')

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_telephone(self, telephone):
        return telephone.isdigit() and len(telephone) == 10

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = Application(root)
    root.mainloop()