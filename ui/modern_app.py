"""
ui/modern_app.py — Application principale moderne "BiblioTech"
---------------------------------------------------------------
Orchestre l'écran de connexion (AuthFrame) et la coquille moderne
(ModernShell). Gère le cycle connexion → app → déconnexion.

C'est le point d'entrée visuel final du projet.
"""

import customtkinter as ctk

from services.book_service import BookService
from chatbot.ai_assistant import AIAssistant
from ui.modern_shell import ModernShell, PAGE_BG


class ModernApp(ctk.CTk):
    """Fenêtre principale : login en façade puis dashboard moderne."""

    def __init__(self):
        super().__init__()
        self.title("BiblioTech — Bibliothèque Intelligente")
        self.geometry("1340x800")
        self.minsize(1100, 680)
        self.configure(fg_color=PAGE_BG)

        # Services partagés
        self.book_service = BookService()
        self.ai_assistant = AIAssistant()

        self.shell = None
        self.auth_frame = None

        self._show_auth()

    def _show_auth(self):
        """Affiche l'écran de connexion."""
        if self.shell is not None:
            self.shell.destroy()
            self.shell = None

        from ui.auth_frame import AuthFrame
        self.auth_frame = AuthFrame(self, on_login_success=self._on_login)
        self.auth_frame.pack(fill="both", expand=True)

    def _on_login(self, user: dict):
        """Connexion réussie → on lance la coquille moderne."""
        if self.auth_frame is not None:
            self.auth_frame.destroy()
            self.auth_frame = None

        self.shell = ModernShell(
            self, self.book_service, user=user,
            on_logout=self._on_logout, ai_assistant=self.ai_assistant,
        )
        self.shell.pack(fill="both", expand=True)

    def _on_logout(self):
        """Déconnexion → retour à l'écran de connexion."""
        self._show_auth()
