"""
ui/stats_frame.py — Tableau de bord et statistiques
-----------------------------------------------------
Cette frame affiche un résumé visuel de la bibliothèque :
cartes de statistiques + liste par catégorie.
"""

import customtkinter as ctk
from services.book_service import BookService


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent, book_service: BookService):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.book_service = book_service
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="📊 Tableau de Bord",
                     font=ctk.CTkFont(size=24, weight="bold")
                     ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 15))

        # Zone scrollable pour tout le contenu
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        scroll.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.scroll = scroll

    def refresh(self):
        """Recharge et affiche les statistiques."""
        # Nettoie le contenu précédent
        for widget in self.scroll.winfo_children():
            widget.destroy()

        stats = self.book_service.get_stats()

        # ── Cartes de statistiques ───────────────────────────────
        # Chaque carte : (titre, valeur, couleur de fond)
        cards = [
            ("📚 Total livres",   stats["total"],       "#1f538d"),
            ("✅ Disponibles",    stats["disponibles"], "#2d7a2d"),
            ("📤 Empruntés",      stats["empruntes"],   "#8b4513"),
            ("🔖 Réservés",       stats["reserves"],    "#4a3a7a"),
        ]

        for i, (label, value, color) in enumerate(cards):
            card = ctk.CTkFrame(self.scroll, fg_color=color, corner_radius=12)
            card.grid(row=0, column=i, padx=8, pady=10, sticky="ew")

            ctk.CTkLabel(card, text=str(value),
                         font=ctk.CTkFont(size=36, weight="bold"),
                         text_color="white"
                         ).pack(pady=(15, 0))

            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(size=13),
                         text_color="white"
                         ).pack(pady=(0, 15))

        # ── Livres par catégorie ─────────────────────────────────
        ctk.CTkLabel(self.scroll, text="Livres par catégorie",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(20, 10))

        categories = self.book_service.get_all_categories()
        for idx, cat in enumerate(categories):
            books = self.book_service.get_books_by_category(cat)
            available = sum(1 for b in books if b.statut == "disponible")

            cat_frame = ctk.CTkFrame(self.scroll, corner_radius=8)
            cat_frame.grid(row=2 + idx // 2, column=(idx % 2) * 2,
                           columnspan=2, padx=8, pady=5, sticky="ew")

            ctk.CTkLabel(cat_frame,
                         text=f"{cat}  ({len(books)} livres · {available} disponibles)",
                         font=ctk.CTkFont(size=13)
                         ).pack(side="left", padx=15, pady=10)

            # Barre de progression : ratio disponibles / total
            if len(books) > 0:
                ratio = available / len(books)
                ctk.CTkProgressBar(cat_frame, width=150
                                   ).pack(side="right", padx=15)
                bar = ctk.CTkProgressBar(cat_frame, width=150)
                bar.set(ratio)
                bar.pack(side="right", padx=15, pady=10)
