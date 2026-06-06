"""
ui/catalogue_frame.py — Écran Catalogue (style moderne "BiblioTech")
---------------------------------------------------------------------
Reproduction en CustomTkinter du visuel de l'application Next.js :
- En-tête avec titre + sous-titre
- Barre de filtres (recherche, catégorie, statut, année)
- Grille scrollable de "cartes-livres" avec badge de statut et chip catégorie

C'est un APERÇU de style : il sert à valider le design avant de
redessiner le reste de l'application.
"""

import customtkinter as ctk
from services.book_service import BookService
from ui.icons import get_icon, load_cover


# ── Palette inspirée du design Next.js (Tailwind) ─────────────────────────────
PAGE_BG     = "#F9FAFB"   # gray-50
CARD_BG     = "#FFFFFF"
BORDER      = "#EEF0F2"   # gray-100
COVER_BG    = "#EFF6FF"   # blue-50
TITLE_CLR   = "#111827"   # gray-900
SUBTLE_CLR  = "#9CA3AF"   # gray-400
MUTED_CLR   = "#6B7280"   # gray-500
CHIP_BG     = "#F3F4F6"   # gray-100
ACCENT      = "#2563EB"   # blue-600
COVER_ICON  = "#BFDBFE"   # blue-200

# Couleurs des badges de statut (fond, texte)
STATUS_STYLE = {
    "disponible": ("#DCFCE7", "#15803D"),  # vert
    "emprunté":   ("#FFEDD5", "#C2410C"),  # orange
    "réservé":    ("#F3E8FF", "#7E22CE"),  # violet
}

GRID_COLUMNS = 5   # nombre de cartes par ligne (plus aéré / minimaliste)

# Proportions "couverture de livre" (ratio ~2/3)
COVER_W = 150
COVER_H = 215


class CatalogueFrame(ctk.CTkFrame):
    """Écran Catalogue : grille de cartes-livres + filtres."""

    def __init__(self, parent, book_service: BookService, on_select=None):
        super().__init__(parent, fg_color=PAGE_BG, corner_radius=0)
        self.book_service = book_service
        self.on_select = on_select          # callback(book) quand une carte est cliquée
        self.all_books = self.book_service.get_all_books()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters()
        self._build_grid()
        self._render_cards(self.all_books)

    # ── En-tête ───────────────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 0))

        ctk.CTkLabel(
            header, text="Catalogue complet",
            font=ctk.CTkFont(size=24, weight="bold"), text_color=TITLE_CLR,
        ).pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            header,
            text=f"Parcourez les {len(self.all_books)} livres de la bibliothèque",
            font=ctk.CTkFont(size=13), text_color=SUBTLE_CLR,
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

    # ── Barre de filtres ──────────────────────────────────────────────────────
    def _build_filters(self):
        bar = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16,
                           border_width=1, border_color=BORDER)
        bar.grid(row=1, column=0, sticky="ew", padx=32, pady=(20, 8))

        # Recherche
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filters())
        search = ctk.CTkEntry(
            bar, textvariable=self.search_var, height=38, width=260,
            corner_radius=10, border_color=BORDER, fg_color="#F9FAFB",
            placeholder_text="🔍  Rechercher titre ou auteur...",
        )
        search.pack(side="left", padx=(14, 10), pady=12)

        # Catégorie
        categories = ["Toutes les catégories"] + sorted({b.categorie for b in self.all_books})
        self.cat_var = ctk.StringVar(value=categories[0])
        ctk.CTkOptionMenu(
            bar, values=categories, variable=self.cat_var,
            command=lambda _: self._apply_filters(),
            height=38, corner_radius=10, fg_color="#F9FAFB",
            button_color="#F9FAFB", button_hover_color="#EFEFEF",
            text_color=MUTED_CLR, dropdown_fg_color=CARD_BG,
        ).pack(side="left", padx=6, pady=12)

        # Statut
        self.status_var = ctk.StringVar(value="Tous les statuts")
        ctk.CTkOptionMenu(
            bar, values=["Tous les statuts", "disponible", "emprunté", "réservé"],
            variable=self.status_var, command=lambda _: self._apply_filters(),
            height=38, corner_radius=10, fg_color="#F9FAFB",
            button_color="#F9FAFB", button_hover_color="#EFEFEF",
            text_color=MUTED_CLR, dropdown_fg_color=CARD_BG,
        ).pack(side="left", padx=6, pady=12)

        # Année
        years = ["Toutes les années"] + [str(y) for y in sorted({b.annee for b in self.all_books}, reverse=True)]
        self.year_var = ctk.StringVar(value=years[0])
        ctk.CTkOptionMenu(
            bar, values=years, variable=self.year_var,
            command=lambda _: self._apply_filters(),
            height=38, corner_radius=10, fg_color="#F9FAFB",
            button_color="#F9FAFB", button_hover_color="#EFEFEF",
            text_color=MUTED_CLR, dropdown_fg_color=CARD_BG,
        ).pack(side="left", padx=6, pady=12)

        # Compteur à droite
        self.count_label = ctk.CTkLabel(bar, text="", text_color=SUBTLE_CLR,
                                        font=ctk.CTkFont(size=12))
        self.count_label.pack(side="right", padx=16)

    # ── Grille scrollable ─────────────────────────────────────────────────────
    def _build_grid(self):
        self.grid_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_area.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 24))
        for c in range(GRID_COLUMNS):
            self.grid_area.grid_columnconfigure(c, weight=1, uniform="cards")

    def refresh(self):
        """Recharge les livres depuis la base et ré-affiche (après un CRUD)."""
        self.all_books = self.book_service.get_all_books()
        self.subtitle_label.configure(
            text=f"Parcourez les {len(self.all_books)} livres de la bibliothèque")
        self._apply_filters()

    def _render_cards(self, books):
        # Nettoie la grille
        for w in self.grid_area.winfo_children():
            w.destroy()

        self.count_label.configure(text=f"{len(books)} livre(s)")

        if not books:
            empty = ctk.CTkLabel(
                self.grid_area, text="Aucun livre ne correspond à vos filtres.",
                text_color=SUBTLE_CLR, font=ctk.CTkFont(size=13),
            )
            empty.grid(row=0, column=0, columnspan=GRID_COLUMNS, pady=60)
            return

        for i, book in enumerate(books):
            row, col = divmod(i, GRID_COLUMNS)
            self._make_card(book).grid(row=row, column=col, padx=10, pady=10, sticky="n")

    # ── Une carte-livre ───────────────────────────────────────────────────────
    def _make_card(self, book):
        card = ctk.CTkFrame(card_parent := self.grid_area, fg_color="transparent",
                            corner_radius=0, width=COVER_W)
        card.pack_propagate(False)
        card.configure(height=COVER_H + 78)

        # Zone "couverture" — épurée, sans bordure (style minimaliste)
        cover = ctk.CTkFrame(card, fg_color=COVER_BG, corner_radius=14,
                             border_width=0, width=COVER_W, height=COVER_H)
        cover.pack()
        cover.pack_propagate(False)

        cover_img = load_cover(book.image_path, (COVER_W, COVER_H), radius=14)
        if cover_img:
            ctk.CTkLabel(cover, text="", image=cover_img,
                         ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(cover, text="", image=get_icon("book", COVER_ICON, 40),
                         ).place(relx=0.5, rely=0.5, anchor="center")

        # Badge de statut (petit point coloré + texte, en haut à droite)
        bg, fg = STATUS_STYLE.get(book.statut, ("#E5E7EB", "#374151"))
        badge = ctk.CTkLabel(
            cover, text=f" {book.statut} ", fg_color=bg, text_color=fg,
            corner_radius=8, font=ctk.CTkFont(size=9, weight="bold"), height=20,
        )
        badge.place(relx=1.0, x=-8, y=8, anchor="ne")

        # Titre
        ctk.CTkLabel(
            card, text=self._truncate(book.titre, 20), anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=TITLE_CLR,
            justify="left",
        ).pack(fill="x", padx=2, pady=(10, 0))

        # Auteur
        ctk.CTkLabel(
            card, text=self._truncate(book.auteur, 24), anchor="w",
            font=ctk.CTkFont(size=10), text_color=SUBTLE_CLR,
        ).pack(fill="x", padx=2, pady=(1, 0))

        # Exemplaires (discret, une seule ligne — plus minimaliste)
        ctk.CTkLabel(
            card, text=f"{book.categorie} · {book.quantite} exempl.", anchor="w",
            font=ctk.CTkFont(size=10), text_color=MUTED_CLR,
        ).pack(fill="x", padx=2, pady=(3, 0))

        # Effet survol : la couverture s'éclaircit légèrement
        def on_enter(_):
            cover.configure(fg_color="#FFFFFF")
        def on_leave(_):
            cover.configure(fg_color=COVER_BG)

        def on_click(_):
            if self.on_select:
                self.on_select(book)

        for w in (card, cover):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return card

    # ── Filtrage ──────────────────────────────────────────────────────────────
    def _apply_filters(self):
        q = self.search_var.get().lower().strip()
        cat = self.cat_var.get()
        status = self.status_var.get()
        year = self.year_var.get()

        def keep(b):
            if q and q not in b.titre.lower() and q not in b.auteur.lower():
                return False
            if cat != "Toutes les catégories" and b.categorie != cat:
                return False
            if status != "Tous les statuts" and b.statut != status:
                return False
            if year != "Toutes les années" and str(b.annee) != year:
                return False
            return True

        self._render_cards([b for b in self.all_books if keep(b)])

    @staticmethod
    def _truncate(text, n):
        return text if len(text) <= n else text[: n - 1] + "…"
