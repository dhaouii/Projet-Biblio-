"""
ui/app.py — Interface graphique principale
------------------------------------------
Ce fichier construit toute l'interface avec CustomTkinter.

Architecture de l'UI :
- BibliothequeApp (fenêtre principale)
  ├── Sidebar (navigation gauche)
  ├── BooksFrame (liste + CRUD)
  ├── ChatFrame (chatbot)
  └── StatsFrame (tableau de bord)

CustomTkinter est une surcouche moderne de Tkinter standard.
Il apporte : mode sombre, coins arrondis, widgets modernes.
"""

import customtkinter as ctk
from services.book_service import BookService
from chatbot.ai_assistant import AIAssistant


# ─── Thème global de l'application ────────────────────────────────────────────
# "dark" = mode sombre activé par défaut
# "blue" = palette de couleurs bleue
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BibliothequeApp(ctk.CTk):
    """
    Fenêtre principale de l'application.
    Hérite de ctk.CTk (fenêtre CustomTkinter).
    """

    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("Bibliothèque Intelligente")
        self.geometry("1280x780")
        self.minsize(1000, 600)

        # Services partagés entre toutes les vues
        self.book_service = BookService()
        self.ai_assistant = AIAssistant()

        # Construction de l'interface
        self._build_layout()
        self._show_frame("books")

    def _build_layout(self):
        """
        Crée la structure principale : sidebar + zone de contenu.
        
        grid() avec columnconfigure(weight=1) → la colonne 1 (contenu)
        prend tout l'espace restant. La colonne 0 (sidebar) reste fixe.
        """
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ─────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)  # Pousse le bas vers le bas

        # Logo/Titre
        ctk.CTkLabel(
            self.sidebar,
            text="📚 BiblioIA",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(30, 10))

        ctk.CTkLabel(
            self.sidebar,
            text="Bibliothèque Intelligente",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=1, column=0, padx=20, pady=(0, 30))

        # Boutons de navigation
        nav_items = [
            ("📖  Livres",      "books"),
            ("🤖  Chatbot IA",  "chat"),
            ("📊  Statistiques","stats"),
        ]
        for i, (label, frame_name) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=40,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda fn=frame_name: self._show_frame(fn)
            )
            btn.grid(row=i + 2, column=0, padx=10, pady=4, sticky="ew")

        # Bouton paramètres API en bas
        ctk.CTkButton(
            self.sidebar,
            text="⚙️  Clé API",
            anchor="w",
            height=35,
            fg_color="transparent",
            text_color="gray60",
            hover_color=("gray70", "gray30"),
            command=self._open_api_settings
        ).grid(row=11, column=0, padx=10, pady=(0, 20), sticky="ew")

        # ── Zone de contenu principal ────────────────────────────
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Préparation des frames (une par section)
        self.frames = {}
        from ui.books_frame import BooksFrame
        from ui.chat_frame import ChatFrame
        from ui.stats_frame import StatsFrame

        self.frames["books"] = BooksFrame(self.content, self.book_service)
        self.frames["chat"]  = ChatFrame(self.content, self.ai_assistant)
        self.frames["stats"] = StatsFrame(self.content, self.book_service)

        # Toutes les frames occupent la même cellule de grille
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def _show_frame(self, name: str):
        """
        Amène la frame demandée au premier plan (tkraise).
        Tkinter empile les frames — on "lève" celle qu'on veut voir.
        """
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            # Rafraîchit les données si la frame a une méthode refresh
            if hasattr(frame, "refresh"):
                frame.refresh()

    def _open_api_settings(self):
        """Ouvre une fenêtre popup pour configurer la clé API Gemini."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configuration API Gemini")
        dialog.geometry("450x200")
        dialog.grab_set()  # Bloque la fenêtre principale

        ctk.CTkLabel(dialog, text="Clé API Google Gemini",
                     font=ctk.CTkFont(size=14, weight="bold")
                     ).pack(pady=(20, 5))

        ctk.CTkLabel(dialog,
                     text="Obtenez votre clé gratuite sur ai.google.dev",
                     text_color="gray60"
                     ).pack()

        entry = ctk.CTkEntry(dialog, width=380, placeholder_text="AIza...",
                             show="*")  # Masque la clé comme un mot de passe
        entry.pack(pady=15)

        # Pré-rempli si une clé existe déjà
        if self.ai_assistant.api_key:
            entry.insert(0, self.ai_assistant.api_key)

        def save():
            key = entry.get().strip()
            self.ai_assistant.set_api_key(key)
            dialog.destroy()

        ctk.CTkButton(dialog, text="Enregistrer", command=save).pack()
