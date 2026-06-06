"""
ui/modern_shell.py — Coquille moderne "BiblioTech" (style Next.js)
-------------------------------------------------------------------
Reproduit en CustomTkinter la mise en page de l'app Next :
- Sidebar gauche (logo, navigation, profil + déconnexion)
- En-tête (bienvenue + recherche)
- Contenu central commutable : Dashboard / Catalogue
- Panneau de détails à droite (bleu nuit)

Réutilise les services existants (BookService) et l'écran Catalogue.
"""

import customtkinter as ctk

from services.book_service import BookService
from ui.icons import get_icon, get_logo, load_cover
from ui.catalogue_frame import (
    CatalogueFrame, PAGE_BG, CARD_BG, BORDER, TITLE_CLR, SUBTLE_CLR,
    MUTED_CLR, ACCENT, STATUS_STYLE,
)

ACTIVE_BG = "#EFF6FF"   # bleu très clair de l'item de nav actif

SIDEBAR_BG = "#FFFFFF"
NAVY_TOP   = "#0A1E5A"   # panneau détails — bleu nuit profond
NAVY_CARD  = "#13317A"   # cartes internes du panneau (couverture, bloc infos)
NAVY_TEXT  = "#9DB8E8"   # texte bleuté clair
NAVY_LABEL = "#7FA3E0"   # libellés / titres de section


class ModernShell(ctk.CTkFrame):
    """Conteneur principal moderne."""

    def __init__(self, parent, book_service: BookService, user: dict | None = None,
                 on_logout=None, ai_assistant=None):
        super().__init__(parent, fg_color=PAGE_BG, corner_radius=0)
        self.book_service = book_service
        self.ai_assistant = ai_assistant
        self.user = user or {"username": "Invité", "role": "user"}
        self.current_user = self.user      # utilisé par BookFormDialog (logging)
        self.on_logout = on_logout
        self.active_page = "Dashboard"
        self.selected_book = None
        self._ready = False                # bloque les refresh pendant la construction

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_center()
        self._build_details_panel()

        # Chatbot flottant (si un assistant est fourni)
        if self.ai_assistant is not None:
            from ui.chat_widget import ChatWidget
            self.chat = ChatWidget(self, self.ai_assistant)

        self._show_page("Dashboard")
        self._ready = True

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        bar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SIDEBAR_BG,
                           border_width=1, border_color=BORDER)
        bar.grid(row=0, column=0, sticky="nsew")
        bar.grid_propagate(False)
        bar.grid_rowconfigure(3, weight=1)

        # Logo : carré bleu arrondi + icône livre blanche au trait
        logo = ctk.CTkFrame(bar, fg_color="transparent")
        logo.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 18))
        mark = ctk.CTkLabel(logo, text="", image=get_logo(42), fg_color="transparent")
        mark.pack(side="left")
        box = ctk.CTkFrame(logo, fg_color="transparent")
        box.pack(side="left", padx=10)
        ctk.CTkLabel(box, text="BiblioTech", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(box, text="Gestion de Bibliothèque", font=ctk.CTkFont(size=10),
                     text_color=SUBTLE_CLR).pack(anchor="w")

        # Navigation
        nav = ctk.CTkFrame(bar, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=12, pady=6)

        items = [("Dashboard", "dashboard", "Dashboard"),
                 ("Catalogue", "catalogue", "Catalogue")]
        if self.user.get("role") == "admin":
            items.append(("Gestion", "gestion", "Gestion"))

        self.nav_buttons = {}   # page_id -> (button, icon_name)
        for page_id, icon_name, label in items:
            btn = ctk.CTkButton(
                nav, text=f"  {label}", image=get_icon(icon_name, MUTED_CLR, 20),
                anchor="w", height=42, corner_radius=10,
                fg_color="transparent", text_color=MUTED_CLR,
                hover_color="#F3F4F6", font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda p=page_id: self._show_page(p),
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[page_id] = (btn, icon_name)

        # Carte profil + déconnexion (en bas)
        profile = ctk.CTkFrame(bar, fg_color="#F9FAFB", corner_radius=12,
                               border_width=1, border_color=BORDER)
        profile.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 8))

        is_admin = self.user.get("role") == "admin"
        avatar = ctk.CTkLabel(
            profile, text="",
            image=get_icon("shield" if is_admin else "user",
                           "#7C3AED" if is_admin else ACCENT, 18),
            width=34, height=34, corner_radius=8,
            fg_color="#EDE9FE" if is_admin else "#DBEAFE",
        )
        avatar.pack(side="left", padx=(10, 8), pady=10)
        info = ctk.CTkFrame(profile, fg_color="transparent")
        info.pack(side="left", pady=10)
        ctk.CTkLabel(info, text=self.user.get("username", "—"),
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(info, text="Administrateur" if is_admin else "Lecteur",
                     font=ctk.CTkFont(size=10), text_color=SUBTLE_CLR).pack(anchor="w")

        # Bouton Clé API Gemini (admin uniquement — clé partagée)
        if is_admin:
            ctk.CTkButton(
                bar, text="  Clé API Gemini", image=get_icon("key", MUTED_CLR, 18),
                anchor="w", height=38, corner_radius=10,
                fg_color="transparent", text_color=MUTED_CLR, hover_color="#F3F4F6",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=self._open_api_settings,
            ).grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 6))

        ctk.CTkButton(
            bar, text="  Déconnexion", image=get_icon("logout", "#DC2626", 20),
            anchor="w", height=40, corner_radius=10,
            fg_color="#FEF2F2", text_color="#DC2626", hover_color="#FEE2E2",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._handle_logout,
        ).grid(row=6, column=0, sticky="ew", padx=12, pady=(0, 18))

    # ── Zone centrale (header + contenu) ──────────────────────────────────────
    def _build_center(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=1, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(center, fg_color="transparent", height=80)
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(22, 6))
        header.grid_columnconfigure(1, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text=f"Bonjour, {self.user.get('username', '')} 👋",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(titles, text="Que souhaitez-vous lire aujourd'hui ?",
                     font=ctk.CTkFont(size=12), text_color=SUBTLE_CLR).pack(anchor="w")

        # Barre de recherche (centrée) — envoie vers le Catalogue
        search_box = ctk.CTkFrame(header, fg_color="#F3F4F6", corner_radius=14,
                                  height=46, width=360)
        search_box.grid(row=0, column=1, padx=20)
        search_box.grid_propagate(False)
        ctk.CTkLabel(search_box, text="", image=get_icon("search", SUBTLE_CLR, 18),
                     ).pack(side="left", padx=(14, 6))
        self.header_search = ctk.CTkEntry(
            search_box, border_width=0, fg_color="transparent", height=44,
            placeholder_text="Rechercher un livre...",
        )
        self.header_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.header_search.bind("<Return>", lambda _e: self._search_from_header())

        ctk.CTkLabel(header, text=self.user.get("username", "U")[:2].upper(),
                     width=40, height=40, corner_radius=12, fg_color=ACCENT,
                     text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                     ).grid(row=0, column=2, padx=8)

        # Conteneur de contenu commutable
        self.content = ctk.CTkFrame(center, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.pages = {}
        self.pages["Dashboard"] = self._build_dashboard()
        self.pages["Catalogue"] = CatalogueFrame(
            self.content, self.book_service, on_select=self._on_select_book)
        if self.user.get("role") == "admin":
            from ui.gestion_frame import GestionFrame
            self.pages["Gestion"] = GestionFrame(
                self.content, self.book_service,
                on_change=self._on_data_changed, parent_app=self)
        # Les pages sont affichées une à la fois via _show_page (grid/grid_remove)

    # ── Dashboard ─────────────────────────────────────────────────────────────
    def _build_dashboard(self):
        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Vue d'ensemble",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TITLE_CLR).grid(row=0, column=0, sticky="w",
                                                padx=8, pady=(4, 16))

        stats = self.book_service.get_stats()
        cards = ctk.CTkFrame(frame, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=4)
        for i in range(3):
            cards.grid_columnconfigure(i, weight=1, uniform="stat")

        stat_defs = [
            ("layers", "#DBEAFE", "#2563EB", "Total des livres", stats.get("total", 0)),
            ("check", "#DCFCE7", "#16A34A", "Disponibles", stats.get("disponibles", 0)),
            ("arrowout", "#FFEDD5", "#EA580C", "Empruntés", stats.get("empruntes", 0)),
        ]
        for i, (icon_name, bg, fg, label, value) in enumerate(stat_defs):
            self._stat_card(cards, icon_name, bg, fg, label, value).grid(
                row=0, column=i, padx=8, sticky="ew")

        # Derniers ajouts
        ctk.CTkLabel(frame, text="Derniers ajouts",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TITLE_CLR).grid(row=2, column=0, sticky="w",
                                                padx=8, pady=(26, 12))

        recent = ctk.CTkFrame(frame, fg_color="transparent")
        recent.grid(row=3, column=0, sticky="ew", padx=4)
        books = self.book_service.get_all_books()[:5]
        for i in range(5):
            recent.grid_columnconfigure(i, weight=1, uniform="recent")
        for i, book in enumerate(books):
            self._mini_book(recent, book).grid(row=0, column=i, padx=8, sticky="n")

        return frame

    def _stat_card(self, parent, icon_name, icon_bg, icon_fg, label, value):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=16,
                            border_width=1, border_color=BORDER, height=96)
        card.pack_propagate(False)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=18)
        ctk.CTkLabel(inner, text="", image=get_icon(icon_name, icon_fg, 24),
                     width=46, height=46, corner_radius=12,
                     fg_color=icon_bg).pack(side="left")
        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", padx=14)
        ctk.CTkLabel(txt, text=label, font=ctk.CTkFont(size=12),
                     text_color=SUBTLE_CLR).pack(anchor="w")
        ctk.CTkLabel(txt, text=str(value), font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        return card

    def _mini_book(self, parent, book):
        card = ctk.CTkFrame(parent, fg_color="transparent", width=150)
        card.pack_propagate(False)
        card.configure(height=250)
        cover = ctk.CTkFrame(card, fg_color="#EFF6FF", corner_radius=14,
                             width=150, height=200)
        cover.pack()
        cover.pack_propagate(False)
        mini_img = load_cover(book.image_path, (150, 200), radius=14)
        if mini_img:
            ctk.CTkLabel(cover, text="", image=mini_img,
                         ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(cover, text="", image=get_icon("book", "#BFDBFE", 38),
                         ).place(relx=0.5, rely=0.5, anchor="center")
        bg, fg = STATUS_STYLE.get(book.statut, ("#E5E7EB", "#374151"))
        ctk.CTkLabel(cover, text=f" {book.statut} ", fg_color=bg, text_color=fg,
                     corner_radius=8, font=ctk.CTkFont(size=9, weight="bold"),
                     height=20).place(relx=1.0, x=-8, y=8, anchor="ne")
        ctk.CTkLabel(card, text=self._truncate(book.titre, 20), anchor="w",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TITLE_CLR).pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(card, text=self._truncate(book.auteur, 24), anchor="w",
                     font=ctk.CTkFont(size=10), text_color=SUBTLE_CLR).pack(fill="x")
        for w in (card, cover):
            w.bind("<Button-1>", lambda _e, b=book: self._on_select_book(b))
        return card

    def _build_placeholder(self, title, subtitle):
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        box = ctk.CTkFrame(frame, fg_color="transparent")
        box.place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TITLE_CLR).pack()
        ctk.CTkLabel(box, text=subtitle, font=ctk.CTkFont(size=13),
                     text_color=SUBTLE_CLR).pack(pady=(8, 0))
        return frame

    # ── Panneau de détails (droite) ───────────────────────────────────────────
    def _build_details_panel(self):
        self.panel = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color=NAVY_TOP)
        self.panel.grid(row=0, column=2, sticky="nsew")
        self.panel.grid_propagate(False)
        self._render_panel(None)

    def _render_panel(self, book):
        for w in self.panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.panel, text="DÉTAILS DU LIVRE",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=NAVY_LABEL).pack(anchor="w", padx=28, pady=(34, 20))

        if not book:
            ctk.CTkLabel(self.panel, text="",
                         image=get_icon("book", "#3B5BA0", 56)).pack(pady=(80, 12))
            ctk.CTkLabel(self.panel, text="Sélectionnez un livre\npour voir les détails",
                         font=ctk.CTkFont(size=12), text_color=NAVY_LABEL,
                         justify="center").pack()
            return

        # Couverture
        cover = ctk.CTkFrame(self.panel, fg_color=NAVY_CARD, corner_radius=18,
                             width=170, height=230)
        cover.pack(pady=(4, 18))
        cover.pack_propagate(False)
        cover_img = load_cover(book.image_path, (170, 230), radius=18)
        if cover_img:
            ctk.CTkLabel(cover, text="", image=cover_img,
                         ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(cover, text="", image=get_icon("book", "#5C7FC9", 60),
                         ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.panel, text=book.titre, font=ctk.CTkFont(size=17, weight="bold"),
                     text_color="white", wraplength=280).pack(padx=20)
        ctk.CTkLabel(self.panel, text=book.auteur, font=ctk.CTkFont(size=12),
                     text_color=NAVY_TEXT).pack(pady=(2, 12))

        bg, fg = STATUS_STYLE.get(book.statut, ("#E5E7EB", "#374151"))
        ctk.CTkLabel(self.panel, text=f"  {book.statut.upper()}  ", fg_color=bg,
                     text_color=fg, corner_radius=10,
                     font=ctk.CTkFont(size=10, weight="bold"), height=24).pack()

        # Bloc infos avec icônes au trait
        info = ctk.CTkFrame(self.panel, fg_color=NAVY_CARD, corner_radius=16)
        info.pack(fill="x", padx=24, pady=20)
        rows = [
            ("hash", "ID Livre", str(book.id)),
            ("bookmark", "Catégorie", book.categorie),
            ("book", "Année", str(book.annee)),
            ("mappin", "Exemplaires", str(book.quantite)),
        ]
        for icon_name, label, value in rows:
            line = ctk.CTkFrame(info, fg_color="transparent")
            line.pack(fill="x", padx=16, pady=8)
            left = ctk.CTkFrame(line, fg_color="transparent")
            left.pack(side="left")
            ctk.CTkLabel(left, text="", image=get_icon(icon_name, NAVY_TEXT, 16),
                         ).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(left, text=label, font=ctk.CTkFont(size=12),
                         text_color=NAVY_TEXT).pack(side="left")
            ctk.CTkLabel(line, text=value, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").pack(side="right", padx=(16, 0))

    # ── Logique ───────────────────────────────────────────────────────────────
    def _show_page(self, page_id):
        self.active_page = page_id
        for pid, (btn, icon_name) in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=ACTIVE_BG, text_color=ACCENT,
                              image=get_icon(icon_name, ACCENT, 20))
            else:
                btn.configure(fg_color="transparent", text_color=MUTED_CLR,
                              image=get_icon(icon_name, MUTED_CLR, 20))
        # Affiche uniquement la page demandée (évite les soucis d'empilement)
        for pid, page in self.pages.items():
            if pid == page_id:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()

    def _search_from_header(self):
        """Bascule sur le Catalogue et applique la recherche saisie en haut."""
        query = self.header_search.get().strip()
        cat = self.pages.get("Catalogue")
        if cat is not None:
            cat.search_var.set(query)   # déclenche le filtrage automatiquement
            self._show_page("Catalogue")

    def _on_select_book(self, book):
        self.selected_book = book
        self._render_panel(book)

    def _on_data_changed(self):
        """Appelé après un CRUD : met à jour catalogue + dashboard."""
        if not self._ready:
            return
        # Catalogue
        cat = self.pages.get("Catalogue")
        if cat and hasattr(cat, "refresh"):
            cat.refresh()
        # Dashboard — reconstruction (stats + derniers ajouts)
        old = self.pages.get("Dashboard")
        if old is not None:
            old.destroy()
            self.pages["Dashboard"] = self._build_dashboard()
            # Réaffiche la page courante (dashboard si actif, sinon il reste caché)
            self._show_page(self.active_page)

    def _open_api_settings(self):
        """Dialog de configuration de la clé API Gemini (clé partagée)."""
        from database.db_manager import DatabaseManager
        db = DatabaseManager()

        dialog = ctk.CTkToplevel(self)
        dialog.title("Configuration API Gemini")
        dialog.geometry("480x300")
        dialog.configure(fg_color=CARD_BG)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # En-tête avec icône clé
        head = ctk.CTkFrame(dialog, fg_color="transparent")
        head.pack(fill="x", padx=28, pady=(26, 6))
        ctk.CTkLabel(head, text="", image=get_icon("key", ACCENT, 22),
                     width=44, height=44, corner_radius=12,
                     fg_color="#DBEAFE").pack(side="left")
        box = ctk.CTkFrame(head, fg_color="transparent")
        box.pack(side="left", padx=12)
        ctk.CTkLabel(box, text="Clé API Google Gemini",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(box, text="Clé partagée utilisée par le chatbot",
                     font=ctk.CTkFont(size=11), text_color=SUBTLE_CLR).pack(anchor="w")

        ctk.CTkLabel(dialog, text="Obtenez une clé gratuite sur ai.google.dev",
                     font=ctk.CTkFont(size=12), text_color=SUBTLE_CLR,
                     ).pack(anchor="w", padx=28, pady=(10, 4))

        entry = ctk.CTkEntry(dialog, height=42, corner_radius=10, show="•",
                             placeholder_text="AIza...", border_color=BORDER)
        entry.pack(fill="x", padx=28)

        current = db.get_api_key("gemini")
        if current:
            entry.insert(0, current)

        status = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12))
        status.pack(anchor="w", padx=28, pady=(6, 0))

        def save():
            key = entry.get().strip()
            if not key:
                status.configure(text="La clé ne peut pas être vide.", text_color="#DC2626")
                return
            db.set_api_key("gemini", key)
            db.log_activity(self.user.get("id"), "update_api_key", "api_key", None,
                            "Mise à jour de la clé API Gemini")
            if self.ai_assistant is not None:
                self.ai_assistant.set_api_key(key)
            status.configure(text="✓ Clé enregistrée et appliquée au chatbot.",
                             text_color="#16A34A")
            dialog.after(900, dialog.destroy)

        btns = ctk.CTkFrame(dialog, fg_color="transparent")
        btns.pack(fill="x", padx=28, pady=18)
        ctk.CTkButton(btns, text="Annuler", width=110, height=40, corner_radius=10,
                      fg_color="transparent", text_color=MUTED_CLR, border_width=1,
                      border_color=BORDER, hover_color="#F3F4F6",
                      command=dialog.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="Enregistrer", width=140, height=40, corner_radius=10,
                      fg_color=ACCENT, hover_color="#1D4ED8",
                      font=ctk.CTkFont(weight="bold"), command=save).pack(side="right")

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()

    @staticmethod
    def _truncate(text, n):
        return text if len(text) <= n else text[: n - 1] + "…"
