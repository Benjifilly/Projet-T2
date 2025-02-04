import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AdminInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface Administrateur")
        self.root.geometry("800x600")
        
        # Connexion à la base de données
        self.conn = sqlite3.connect('D:\Projet-T2-main\Sallemuscu.db')
        self.cursor = self.conn.cursor()
        
        # Création des onglets
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Création des frames pour chaque table
        self.tables = ['Creneau', 'Equipement', 'Liste_attente', 'Reservation', 'Utilisateur']
        self.frames = {}
        
        for table in self.tables:
            self.frames[table] = ttk.Frame(self.notebook)
            self.notebook.add(self.frames[table], text=table)
            self.setup_table_frame(table)
            
        # Boutons généraux
        self.setup_general_buttons()

    def setup_general_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Supprimer toutes les données", 
                  command=self.delete_all_data).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Sauvegarder BDD", 
                  command=self.backup_database).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Statistiques", 
                  command=self.show_statistics).pack(side='left', padx=5)

    def setup_table_frame(self, table_name):
        frame = self.frames[table_name]
        
        # Treeview pour afficher les données
        columns = self.get_table_columns(table_name)
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Boutons CRUD
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Ajouter", 
                  command=lambda: self.add_record(table_name)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Modifier", 
                  command=lambda: self.edit_record(table_name, tree)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Supprimer", 
                  command=lambda: self.delete_record(table_name, tree)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Supprimer toute la table", 
                  command=lambda: self.delete_table_data(table_name, tree)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Actualiser", 
                  command=lambda: self.refresh_table(table_name, tree)).pack(side='left', padx=2)
        
        # Recherche
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text="Rechercher:").pack(side='left', padx=2)
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side='left', padx=2, expand=True, fill='x')
        search_entry.bind('<KeyRelease>', lambda e: self.search_records(table_name, tree, search_entry.get()))
        
        # Initial data load
        self.refresh_table(table_name, tree)

    def get_table_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [col[1] for col in self.cursor.fetchall()]

    def refresh_table(self, table_name, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        self.cursor.execute(f"SELECT * FROM {table_name}")
        for row in self.cursor.fetchall():
            tree.insert('', 'end', values=row)

    def add_record(self, table_name):
        # Création d'une nouvelle fenêtre pour l'ajout
        add_window = tk.Toplevel(self.root)
        add_window.title(f"Ajouter - {table_name}")
        
        columns = self.get_table_columns(table_name)
        entries = {}
        
        for col in columns:
            frame = ttk.Frame(add_window)
            frame.pack(fill='x', padx=5, pady=2)
            ttk.Label(frame, text=col).pack(side='left')
            entry = ttk.Entry(frame)
            entry.pack(side='left', padx=5)
            entries[col] = entry
        
        def save():
            values = [entries[col].get() for col in columns]
            placeholders = ','.join(['?' for _ in columns])
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            
            try:
                self.cursor.execute(query, values)
                self.conn.commit()
                messagebox.showinfo("Succès", "Enregistrement ajouté avec succès!")
                add_window.destroy()
                self.refresh_table(table_name, self.notebook.select())
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", str(e))
        
        ttk.Button(add_window, text="Sauvegarder", command=save).pack(pady=5)

    def edit_record(self, table_name, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un enregistrement à modifier")
            return
            
        item = tree.item(selected[0])
        values = item['values']
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Modifier - {table_name}")
        
        columns = self.get_table_columns(table_name)
        entries = {}
        
        for i, col in enumerate(columns):
            frame = ttk.Frame(edit_window)
            frame.pack(fill='x', padx=5, pady=2)
            ttk.Label(frame, text=col).pack(side='left')
            entry = ttk.Entry(frame)
            entry.insert(0, values[i])
            entry.pack(side='left', padx=5)
            entries[col] = entry
        
        def save():
            new_values = [entries[col].get() for col in columns]
            set_clause = ','.join([f"{col}=?" for col in columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]}=?"
            
            try:
                self.cursor.execute(query, new_values + [values[0]])
                self.conn.commit()
                messagebox.showinfo("Succès", "Enregistrement modifié avec succès!")
                edit_window.destroy()
                self.refresh_table(table_name, tree)
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", str(e))
        
        ttk.Button(edit_window, text="Sauvegarder", command=save).pack(pady=5)

    def delete_record(self, table_name, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un enregistrement à supprimer")
            return
            
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet enregistrement?"):
            item = tree.item(selected[0])
            id_value = item['values'][0]
            
            try:
                self.cursor.execute(f"DELETE FROM {table_name} WHERE {self.get_table_columns(table_name)[0]}=?", (id_value,))
                self.conn.commit()
                messagebox.showinfo("Succès", "Enregistrement supprimé avec succès!")
                self.refresh_table(table_name, tree)
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", str(e))

    def delete_all_data(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer TOUTES les données?"):
            try:
                for table in self.tables:
                    self.cursor.execute(f"DELETE FROM {table}")
                self.conn.commit()
                messagebox.showinfo("Succès", "Toutes les données ont été supprimées!")
                self.refresh_all_tables()
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", str(e))

    def delete_table_data(self, table_name, tree):
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer TOUTES les données de la table {table_name}?"):
            try:
                self.cursor.execute(f"DELETE FROM {table_name}")
                self.conn.commit()
                messagebox.showinfo("Succès", f"Toutes les données de la table {table_name} ont été supprimées!")
                self.refresh_table(table_name, tree)
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", str(e))

    def backup_database(self):
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            backup_conn = sqlite3.connect(backup_name)
            self.conn.backup(backup_conn)
            backup_conn.close()
            messagebox.showinfo("Succès", f"Sauvegarde créée: {backup_name}")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", str(e))

    def show_statistics(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistiques")
        stats_window.geometry("400x300")
        
        text = tk.Text(stats_window, wrap=tk.WORD)
        text.pack(expand=True, fill='both', padx=10, pady=10)
        
        for table in self.tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                text.insert('end', f"{table}: {count} enregistrements\n")
                
                # Statistiques spécifiques par table
                if table == 'Reservation':
                    self.cursor.execute("SELECT Statut, COUNT(*) FROM Reservation GROUP BY Statut")
                    for status, status_count in self.cursor.fetchall():
                        text.insert('end', f"  - Status {status}: {status_count}\n")
                        
                elif table == 'Equipement':
                    self.cursor.execute("SELECT Disponibilite, COUNT(*) FROM Equipement GROUP BY Disponibilite")
                    for dispo, dispo_count in self.cursor.fetchall():
                        text.insert('end', f"  - Disponibilité {dispo}: {dispo_count}\n")
            except sqlite3.Error as e:
                text.insert('end', f"Erreur pour {table}: {str(e)}\n")
        
        text.config(state='disabled')

    def search_records(self, table_name, tree, search_text):
        for item in tree.get_children():
            tree.delete(item)
            
        columns = self.get_table_columns(table_name)
        search_conditions = ' OR '.join([f"{col} LIKE ?" for col in columns])
        query = f"SELECT * FROM {table_name} WHERE {search_conditions}"
        search_params = [f"%{search_text}%" for _ in columns]
        
        try:
            self.cursor.execute(query, search_params)
            for row in self.cursor.fetchall():
                tree.insert('', 'end', values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de recherche", str(e))

    def refresh_all_tables(self):
        for table in self.tables:
            for widget in self.frames[table].winfo_children():
                if isinstance(widget, ttk.Treeview):
                    self.refresh_table(table, widget)

if __name__ == '__main__':
    root = tk.Tk()
    app = AdminInterface(root)
    root.mainloop()