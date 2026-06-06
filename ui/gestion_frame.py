"""
ui/gestion_frame.py — Écran Gestion (CRUD admin) au style moderne
------------------------------------------------------------------
Liste des livres sous forme de lignes-cartes avec :
- Barre de filtres (recherche ID/titre/auteur, catégorie, statut)
- Actions ➕ Ajouter / ✏️ Modifier / 🗑 Supprimer

Réutilise BookFormDialog (formulaire existant) et BookService.
"""

import customtkinter as ctk
from tkinter import messagebox

from services.book_service import BookService
from ui.books_frame import BookFormDialog
from ui.icons import get_icon, load_cover
from ui.catalogue_frame import (
    PAGE_BG, CARD_BG, BORDER, TITLE_CLR, SUBTLE_CLR, MUTED_CLR, ACCENT,
    CHIP_BG, STATUS_STYLE,
)


class GestionFrame(ctk.CTkFrame):
    """Écran d'administration des livres (CRUD + filtres)."""

    def __init__(self, parent, book_service: BookService, on_change=None,
                 parent_app=None):
        super().__init__(parent, fg_color=PAGE_BG, corner_radius=0)
        self.book_service = book_service
        self.on_change = on_change      # callback() pour notifier le shell
        self.parent_app = parent_app
        self.all_books = self.book_service.get_all_books()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters()

        self.list_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_area.grid(row=2, column=0, sticky="nsew", padx=24, pady=(8, 24))
        self.list_area.grid_columnconfigure(0, weight=1)

        self._apply_filters()

    # ── En-tête ───────────────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 0))
        header.grid_columnconfigure(0, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text="Gestion des livres",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(titles, text="Ajouter, modifier ou supprimer des livres (Admin)",
                     font=ctk.CTkFont(size=13), text_color=SUBTLE_CLR).pack(anchor="w")

        ctk.CTkButton(
            header, text="  Ajouter un livre", image=get_icon("plus", "#FFFFFF", 18),
            height=42, corner_radius=10, fg_color=ACCENT, hover_color="#1D4ED8",
            font=ctk.CTkFont(size=13, weight="bold"), command=self._add,
        ).grid(row=0, column=1, sticky="e")

    # ── Barre de filtres ──────────────────────────────────────────────────────
    def _build_filters(self):
        bar = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16,
                           border_width=1, border_color=BORDER)
        bar.grid(row=1, column=0, sticky="ew", padx=24, pady=(18, 6))

        # Recherche (ID, titre, auteur)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filters())
        ctk.CTkLabel(bar, text="", image=get_icon("search", SUBTLE_CLR, 16),
                     ).pack(side="left", padx=(14, 2), pady=12)
        ctk.CTkEntry(
            bar, textvariable=self.search_var, height=38, width=240,
            corner_radius=10, border_color=BORDER, fg_color="#F9FAFB",
            placeholder_text="Rechercher (ID, titre, auteur)...",
        ).pack(side="left", padx=(4, 10), pady=12)

        # Catégorie
        self.cat_var = ctk.StringVar(value="Toutes catégories")
        self.cat_menu = ctk.CTkOptionMenu(
            bar, values=self._category_values(), variable=self.cat_var,
            command=lambda _: self._apply_filters(),
            height=38, corner_radius=10, fg_color="#F9FAFB",
            button_color="#F9FAFB", button_hover_color="#EFEFEF",
            text_color=MUTED_CLR, dropdown_fg_color=CARD_BG,
        )
        self.cat_menu.pack(side="left", padx=6, pady=12)

        # Statut
        self.status_var = ctk.StringVar(value="Tous statuts")
        ctk.CTkOptionMenu(
            bar, values=["Tous statuts", "disponible", "emprunté", "réservé"],
            variable=self.status_var, command=lambda _: self._apply_filters(),
            height=38, corner_radius=10, fg_color="#F9FAFB",
            button_color="#F9FAFB", button_hover_color="#EFEFEF",
            text_color=MUTED_CLR, dropdown_fg_color=CARD_BG,
        ).pack(side="left", padx=6, pady=12)

        # Compteur
        self.count_label = ctk.CTkLabel(bar, text="", text_color=SUBTLE_CLR,
                                        font=ctk.CTkFont(size=12))
        self.count_label.pack(side="right", padx=16)

    def _category_values(self):
        return ["Toutes catégories"] + sorted({b.categorie for b in self.all_books})

    # ── Filtrage + rendu ──────────────────────────────────────────────────────
    def _apply_filters(self):
        q = self.search_var.get().lower().strip()
        cat = self.cat_var.get()
        status = self.status_var.get()

        def keep(b):
            if q:
                haystack = f"{b.id} {b.titre} {b.auteur} {b.categorie}".lower()
                if q not in haystack:
                    return False
            if cat != "Toutes catégories" and b.categorie != cat:
                return False
            if status != "Tous statuts" and b.statut != status:
                return False
            return True

        self._render_rows([b for b in self.all_books if keep(b)])

    def _render_rows(self, books):
        for w in self.list_area.winfo_children():
            w.destroy()

        self.count_label.configure(text=f"{len(books)} livre(s)")

        if not books:
            ctk.CTkLabel(self.list_area, text="Aucun livre ne correspond aux filtres.",
                         text_color=SUBTLE_CLR, font=ctk.CTkFont(size=13)).pack(pady=40)
            return

        for book in books:
            self._row(book).pack(fill="x", pady=5)

    def refresh(self):
        """Recharge depuis la base, met à jour les filtres et ré-affiche."""
        self.all_books = self.book_service.get_all_books()
        # Met à jour les catégories disponibles (en gardant la sélection si possible)
        values = self._category_values()
        self.cat_menu.configure(values=values)
        if self.cat_var.get() not in values:
            self.cat_var.set("Toutes catégories")
        self._apply_filters()
        if self.on_change:
            self.on_change()

    # ── Ligne-carte d'un livre ────────────────────────────────────────────────
    def _row(self, book):
        row = ctk.CTkFrame(self.list_area, fg_color=CARD_BG, corner_radius=14,
                           border_width=1, border_color=BORDER)
        row.grid_columnconfigure(1, weight=1)

        # Mini couverture
        cover = ctk.CTkFrame(row, fg_color="#EFF6FF", corner_radius=10,
                             width=44, height=58)
        cover.grid(row=0, column=0, padx=14, pady=12)
        cover.grid_propagate(False)
        row_img = load_cover(book.image_path, (44, 58), radius=10)
        if row_img:
            ctk.CTkLabel(cover, text="", image=row_img,
                         ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(cover, text="", image=get_icon("book", "#BFDBFE", 22),
                         ).place(relx=0.5, rely=0.5, anchor="center")

        # Infos
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", pady=12)
        ctk.CTkLabel(info, text=f"#{book.id}  {book.titre}", anchor="w",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(info, text=book.auteur, anchor="w",
                     font=ctk.CTkFont(size=11), text_color=SUBTLE_CLR).pack(anchor="w")

        meta = ctk.CTkFrame(info, fg_color="transparent")
        meta.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(meta, text=f" {book.categorie} ", fg_color=CHIP_BG,
                     text_color=MUTED_CLR, corner_radius=8,
                     font=ctk.CTkFont(size=10, weight="bold"), height=20).pack(side="left")
        bg, fg = STATUS_STYLE.get(book.statut, ("#E5E7EB", "#374151"))
        ctk.CTkLabel(meta, text=f" {book.statut} ", fg_color=bg, text_color=fg,
                     corner_radius=8, font=ctk.CTkFont(size=10, weight="bold"),
                     height=20).pack(side="left", padx=6)
        ctk.CTkLabel(meta, text=f"{book.annee} · {book.quantite} exempl.",
                     text_color=SUBTLE_CLR, font=ctk.CTkFont(size=10)).pack(side="left", padx=4)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=2, padx=14)
        ctk.CTkButton(
            actions, text=" Modifier", image=get_icon("pencil", ACCENT, 16),
            width=104, height=34, corner_radius=8, fg_color="transparent",
            text_color=ACCENT, hover_color="#EFF6FF", border_width=1,
            border_color=ACCENT, font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda b=book: self._edit(b),
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            actions, text=" Supprimer", image=get_icon("trash", "#DC2626", 16),
            width=110, height=34, corner_radius=8, fg_color="transparent",
            text_color="#DC2626", hover_color="#FEF2F2", border_width=1,
            border_color="#FCA5A5", font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda b=book: self._delete(b),
        ).pack(side="left", padx=4)

        return row

    # ── Actions CRUD ──────────────────────────────────────────────────────────
    def _add(self):
        BookFormDialog(self, self.book_service, mode="add",
                       on_success=self.refresh, parent_app=self.parent_app)

    def _edit(self, book):
        BookFormDialog(self, self.book_service, mode="edit", book_id=book.id,
                       on_success=self.refresh, parent_app=self.parent_app)

    def _delete(self, book):
        if messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer « {book.titre} » ?\nCette action est irréversible.",
        ):
            success, msg = self.book_service.delete_book(book.id)
            if success:
                self.refresh()
            else:
                messagebox.showerror("Erreur", msg)
