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

    def __init__(self, parent, book_service: BookService):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.book_service = book_service
        self.selected_book_id = None  # ID du livre sélectionné dans le tableau
        self._build()

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
        # self.search_var.trace("w", self._on_search) 
        search_entry = ctk.CTkEntry(header, textvariable=self.search_var,
                                    placeholder_text="🔍 Rechercher et appuyez sur Entrée...",
                                    width=250)
        search_entry.grid(row=0, column=1, padx=20, sticky="e")
        search_entry.bind("<Return>", self._on_search)
        # Bouton Ajouter
        ctk.CTkButton(header, text="+ Ajouter un livre",
                      command=self._open_add_dialog,
                      width=150
                      ).grid(row=0, column=2)

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

        # Style sombre pour le tableau
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background="#2b2b2b",
                         foreground="white",
                         rowheight=28,
                         fieldbackground="#2b2b2b",
                         bordercolor="#3d3d3d",
                         borderwidth=0)
        style.configure("Treeview.Heading",
                         background="#1f538d",
                         foreground="white",
                         relief="flat")
        style.map("Treeview",
                  background=[("selected", "#1f538d")],
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

        ctk.CTkButton(actions, text="✏️ Modifier",
                      command=self._open_edit_dialog,
                      fg_color="#2d7a2d", hover_color="#1f5a1f"
                      ).pack(side="left", padx=5)

        ctk.CTkButton(actions, text="🗑 Supprimer",
                      command=self._delete_selected,
                      fg_color="#8b0000", hover_color="#5c0000"
                      ).pack(side="left", padx=5)

        # Compteur de livres affichés
        self.count_label = ctk.CTkLabel(actions, text="", text_color="gray60")
        self.count_label.pack(side="right")

        # Chargement initial des données
        self.refresh()

    def refresh(self):
        """Recharge les données depuis la base et met à jour le tableau."""
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
        # Efface toutes les lignes existantes
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Couleurs selon le statut
        tag_colors = {
            "disponible": "#2d7a2d",
            "emprunté":   "#8b4513",
            "réservé":    "#1a4a7a",
        }

        for book in books:
            tag = book.statut
            self.tree.insert("", "end",
                             values=(book.id, book.titre, book.auteur,
                                     book.categorie, book.annee,
                                     book.quantite, book.statut),
                             tags=(tag,))

        # Applique les couleurs de fond selon le statut
        # Couleurs de fond pastel adaptées à chaque statut
        status_backgrounds = {
            "Disponible": "#e6f4ea",      # Vert clair
            "Emprunté": "#feeeee",        # Rouge clair
            "En retard": "#fef7e0",       # Jaune clair
            "Réservé": "#e8f0fe"          # Bleu clair
        }

        # Applique les couleurs de fond selon le statut
        for status, color in tag_colors.items():
            bg_color = status_backgrounds.get(status, color)
            self.tree.tag_configure(status, background=bg_color)

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
                messagebox.showinfo("Succès", msg)
                self.selected_book_id = None
                self.refresh()
            else:
                messagebox.showerror("Erreur", msg)

    def _open_add_dialog(self):
        """Ouvre le formulaire d'ajout de livre."""
        BookFormDialog(self, self.book_service, mode="add",
                       on_success=self.refresh)

    def _open_edit_dialog(self):
        """Ouvre le formulaire de modification avec les données existantes."""
        if not self.selected_book_id:
            messagebox.showwarning("Attention", "Sélectionnez un livre à modifier.")
            return
        BookFormDialog(self, self.book_service, mode="edit",
                       book_id=self.selected_book_id,
                       on_success=self.refresh)


class BookFormDialog(ctk.CTkToplevel):
    """
    Formulaire modal pour ajouter ou modifier un livre.
    
    Mode 'add'  → formulaire vide
    Mode 'edit' → formulaire pré-rempli avec les données existantes
    
    Paramètre on_success : callback appelé après succès
    pour rafraîchir le tableau parent.
    """

    def __init__(self, parent, book_service: BookService,
                 mode="add", book_id=None, on_success=None):
        super().__init__(parent)
        self.book_service = book_service
        self.mode = mode
        self.book_id = book_id
        self.on_success = on_success

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
        else:
            success, msg = self.book_service.update_book(
                self.book_id, data["titre"], data["auteur"], data["categorie"],
                data["annee"], data["quantite"], data["statut"]
            )

        if success:
            messagebox.showinfo("Succès", msg)
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Erreur de validation", msg)
