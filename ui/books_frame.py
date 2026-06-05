"""
ui/books_frame.py — Interface de gestion des livres (CRUD)
-----------------------------------------------------------
Ce fichier contient toute la logique visuelle pour :
- Afficher la liste des livres dans un tableau
- Ajouter, modifier, supprimer un livre
- Rechercher et filtrer
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from services.book_service import BookService


class BooksFrame(ctk.CTkFrame):
    """
    Frame principale pour la gestion des livres.
    Hérite de ctk.CTkFrame — c'est un widget conteneur.
    """

    def __init__(self, parent, book_service: BookService, parent_app=None):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.book_service = book_service
        self.selected_book_id = None
        self.parent_app = parent_app
        self.admin_buttons = []
        self._build()

    @property
    def is_admin(self):
        """Vérifie si l'utilisateur courant est admin."""
        if self.parent_app and hasattr(self.parent_app, 'current_user'):
            return self.parent_app.current_user and self.parent_app.current_user.get('role') == 'admin'
        return False

    def _build(self):
        """Construit tous les widgets de cette frame."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── En-tête ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, height=60, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Gestion des Livres",
                     font=ctk.CTkFont(size=24, weight="bold")
                     ).grid(row=0, column=0, sticky="w")

        # Barre de recherche
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(header, textvariable=self.search_var,
                                    placeholder_text="🔍 Rechercher et appuyez sur Entrée...",
                                    width=250)
        search_entry.grid(row=0, column=1, padx=20, sticky="e")
        search_entry.bind("<Return>", self._on_search)

        # Bouton Ajouter (admin only)
        self.add_button = ctk.CTkButton(header, text="+ Ajouter un livre",
                      command=self._open_add_dialog,
                      width=150)
        self.add_button.grid(row=0, column=2)
        self.admin_buttons.append(self.add_button)

        # ── Tableau des livres ───────────────────────────────────
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # ttk.Treeview = widget tableau natif Tkinter
        # Columns = identifiants internes des colonnes
        columns = ("id", "titre", "auteur", "categorie", "annee", "quantite", "statut")
        self.tree = ttk.Treeview(table_frame, columns=columns,
                                  show="headings", selectmode="browse")

        # Configuration de chaque colonne (largeur + en-tête)
        col_config = {
            "id":        ("ID",         50),
            "titre":     ("Titre",      250),
            "auteur":    ("Auteur",     180),
            "categorie": ("Catégorie",  120),
            "annee":     ("Année",       70),
            "quantite":  ("Qté",         50),
            "statut":    ("Statut",     100),
        }
        for col, (heading, width) in col_config.items():
            self.tree.heading(col, text=heading,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=width, anchor="center" if width < 150 else "w")

        # Style minimaliste Apple pour le tableau
        style = ttk.Style()
        style.theme_use("clam")
        
        # Le fond est géré automatiquement par ctk, mais on s'assure que le tableau est propre
        style.configure("Treeview",
                         background="white",
                         foreground="black",
                         rowheight=35, # Lignes plus espacées
                         fieldbackground="white",
                         bordercolor="#e5e5e5",
                         borderwidth=0,
                         font=("Helvetica", 12))
        
        style.configure("Treeview.Heading",
                         background="#f5f5f7",
                         foreground="gray40",
                         relief="flat",
                         font=("Helvetica", 12, "bold"))
                         
        style.map("Treeview",
                  background=[("selected", "#0A84FF")], # Bleu Apple
                  foreground=[("selected", "white")])

        # Scrollbar verticale
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Événement : clic sur une ligne du tableau
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-Button-1>", lambda e: self._open_edit_dialog())

        # ── Barre d'actions bas ──────────────────────────────────
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))

        # Admin-only buttons (created but visibility managed dynamically)
        self.edit_button = ctk.CTkButton(actions, text="✏️ Modifier",
                      command=self._open_edit_dialog,
                      fg_color="transparent", text_color="#0A84FF",
                      hover_color=("gray90", "gray20"),
                      border_width=1, border_color="#0A84FF",
                      corner_radius=8)
        self.edit_button.pack(side="left", padx=5)
        self.admin_buttons.append(self.edit_button)

        self.delete_button = ctk.CTkButton(actions, text="🗑 Supprimer",
                      command=self._delete_selected,
                      fg_color="transparent", text_color="#ff3b30",
                      hover_color=("gray90", "gray20"),
                      border_width=1, border_color="#ff3b30",
                      corner_radius=8)
        self.delete_button.pack(side="left", padx=5)
        self.admin_buttons.append(self.delete_button)

        self.readonly_label = ctk.CTkLabel(actions, text="📖 Lecture seule - Les admins peuvent modifier les livres",
                         text_color="gray60", font=ctk.CTkFont(size=11))
        self.readonly_label.pack(side="left", padx=5)

        # Compteur de livres affichés
        self.count_label = ctk.CTkLabel(actions, text="", text_color="gray60")
        self.count_label.pack(side="right")

        # Mise à jour de la visibilité
        self._update_admin_visibility()

        # Chargement initial des données
        self.refresh()

    def _update_admin_visibility(self):
        """Met à jour la visibilité des boutons admin."""
        if self.is_admin:
            self.add_button.grid()
            self.edit_button.pack(side="left", padx=5)
            self.delete_button.pack(side="left", padx=5)
            self.readonly_label.pack_forget()
        else:
            self.add_button.grid_remove()
            self.edit_button.pack_forget()
            self.delete_button.pack_forget()
            self.readonly_label.pack(side="left", padx=5)

    def refresh(self):
        """Recharge les données depuis la base et met à jour le tableau."""
        self._update_admin_visibility()
        query = self.search_var.get() if hasattr(self, "search_var") else ""
        books = (self.book_service.search_books(query) if query
                 else self.book_service.get_all_books())
        self._populate_table(books)

    def _populate_table(self, books):
        """
        Remplit le tableau avec une liste de livres.
        
        On efface d'abord toutes les lignes (delete(*children))
        puis on réinsère — approche simple et fiable.
        """
        # On efface toutes les lignes existantes
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Statuts avec Emojis pour le minimalisme (Apple UI style)
        status_formatting = {
            "disponible": "🟢 Disponible",
            "emprunté":   "🔴 Emprunté",
            "réservé":    "🟡 Réservé",
        }

        for i, book in enumerate(books):
            formatted_status = status_formatting.get(book.statut, book.statut)
            
            # Alternance de couleurs subtile (zebra striping) pour lisibilité
            tag = "even" if i % 2 == 0 else "odd"
            
            self.tree.insert("", "end",
                             values=(book.id, book.titre, book.auteur,
                                     book.categorie, book.annee,
                                     book.quantite, formatted_status),
                             tags=(tag,))

        # Couleurs de fond alternées (très subtil)
        self.tree.tag_configure("even", background="#ffffff") # Blanc pur
        self.tree.tag_configure("odd", background="#f9f9f9")  # Gris très très clair

        count = len(books)
        self.count_label.configure(text=f"{count} livre{'s' if count > 1 else ''} affiché{'s' if count > 1 else ''}")

    def _on_search(self, *args):
        """Déclenché automatiquement à chaque changement dans la barre de recherche."""
        self.refresh()

    def _on_select(self, event):
        """Mémorise l'ID du livre sélectionné dans le tableau."""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0])["values"]
            self.selected_book_id = values[0]  # La première colonne = ID

    def _sort_by(self, col):
        """Tri par colonne (clic sur l'en-tête)."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort()
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

    def _delete_selected(self):
        """Supprime le livre sélectionné après confirmation."""
        if not self.selected_book_id:
            messagebox.showwarning("Attention", "Sélectionnez un livre à supprimer.")
            return

        confirmed = messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer le livre ID {self.selected_book_id} ?\nCette action est irréversible."
        )
        if confirmed:
            success, msg = self.book_service.delete_book(self.selected_book_id)
            if success:
                if self.parent_app and hasattr(self.parent_app, 'current_user'):
                    from database.db_manager import DatabaseManager
                    db = DatabaseManager()
                    db.log_activity(
                        self.parent_app.current_user['id'],
                        'delete_book',
                        'book',
                        self.selected_book_id,
                        f"Suppression du livre {self.selected_book_id}"
                    )
                messagebox.showinfo("Succès", msg)
                self.selected_book_id = None
                self.refresh()
            else:
                messagebox.showerror("Erreur", msg)

    def _open_add_dialog(self):
        """Ouvre le formulaire d'ajout de livre."""
        BookFormDialog(self, self.book_service, mode="add",
                       on_success=self.refresh, parent_app=self.parent_app)

    def _open_edit_dialog(self):
        """Ouvre le formulaire de modification avec les données existantes."""
        if not self.selected_book_id:
            messagebox.showwarning("Attention", "Sélectionnez un livre à modifier.")
            return
        BookFormDialog(self, self.book_service, mode="edit",
                       book_id=self.selected_book_id,
                       on_success=self.refresh, parent_app=self.parent_app)


class BookFormDialog(ctk.CTkToplevel):
    """
    Formulaire modal pour ajouter ou modifier un livre.
    
    Mode 'add'  → formulaire vide
    Mode 'edit' → formulaire pré-rempli avec les données existantes
    
    Paramètre on_success : callback appelé après succès
    pour rafraîchir le tableau parent.
    """

    def __init__(self, parent, book_service: BookService,
                 mode="add", book_id=None, on_success=None, parent_app=None):
        super().__init__(parent)
        self.book_service = book_service
        self.mode = mode
        self.book_id = book_id
        self.on_success = on_success
        self.parent_app = parent_app

        title = "Ajouter un livre" if mode == "add" else "Modifier le livre"
        self.title(title)
        self.geometry("500x520")
        self.grab_set()  # Bloque la fenêtre principale
        self.resizable(False, False)

        self._build()

        # En mode édition, on charge les données existantes
        if mode == "edit" and book_id:
            self._load_book_data()

    def _build(self):
        """Construit le formulaire."""
        ctk.CTkLabel(self, text=self.title(),
                     font=ctk.CTkFont(size=18, weight="bold")
                     ).pack(pady=(20, 15))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # Champs du formulaire : (label, attribut, placeholder)
        fields = [
            ("Titre *",             "titre",     "Ex: Les Misérables"),
            ("Auteur *",            "auteur",    "Ex: Victor Hugo"),
            ("Catégorie *",         "categorie", "Ex: Roman, Science..."),
            ("Année de publication","annee",     "Ex: 1862"),
            ("Quantité disponible", "quantite",  "Ex: 3"),
        ]

        self.entries = {}
        for label_text, attr, placeholder in fields:
            ctk.CTkLabel(form, text=label_text, anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, placeholder_text=placeholder)
            entry.pack(fill="x")
            self.entries[attr] = entry

        # Menu déroulant pour le statut
        ctk.CTkLabel(form, text="Statut", anchor="w").pack(fill="x", pady=(8, 2))
        self.statut_var = ctk.StringVar(value="disponible")
        ctk.CTkOptionMenu(form,
                          values=["disponible", "emprunté", "réservé"],
                          variable=self.statut_var
                          ).pack(fill="x")

        # Bouton de soumission
        btn_text = "Ajouter" if self.mode == "add" else "Enregistrer"
        ctk.CTkButton(self, text=btn_text,
                      command=self._submit, height=40
                      ).pack(pady=20, padx=30, fill="x")

    def _load_book_data(self):
        """Pré-remplit le formulaire avec les données du livre existant."""
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        book = db.get_book_by_id(self.book_id)
        if book:
            self.entries["titre"].insert(0, book.titre)
            self.entries["auteur"].insert(0, book.auteur)
            self.entries["categorie"].insert(0, book.categorie)
            self.entries["annee"].insert(0, str(book.annee))
            self.entries["quantite"].insert(0, str(book.quantite))
            self.statut_var.set(book.statut)

    def _submit(self):
        """Valide et soumet le formulaire (ajout ou modification)."""
        data = {k: v.get() for k, v in self.entries.items()}
        data["statut"] = self.statut_var.get()

        if self.mode == "add":
            success, msg = self.book_service.add_book(
                data["titre"], data["auteur"], data["categorie"],
                data["annee"], data["quantite"], data["statut"]
            )
            if success and self.parent_app and hasattr(self.parent_app, 'current_user'):
                from database.db_manager import DatabaseManager
                db = DatabaseManager()
                db.log_activity(
                    self.parent_app.current_user['id'],
                    'add_book',
                    'book',
                    None,
                    f"Ajout du livre '{data['titre']}' par {data['auteur']}"
                )
        else:
            success, msg = self.book_service.update_book(
                self.book_id, data["titre"], data["auteur"], data["categorie"],
                data["annee"], data["quantite"], data["statut"]
            )
            if success and self.parent_app and hasattr(self.parent_app, 'current_user'):
                from database.db_manager import DatabaseManager
                db = DatabaseManager()
                db.log_activity(
                    self.parent_app.current_user['id'],
                    'update_book',
                    'book',
                    self.book_id,
                    f"Modification du livre '{data['titre']}'"
                )

        if success:
            messagebox.showinfo("Succès", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Erreur de validation", msg)
