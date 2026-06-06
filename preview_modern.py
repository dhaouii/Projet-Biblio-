"""
preview_modern.py — Aperçu de l'app moderne complète
-----------------------------------------------------
Lance la coquille moderne "BiblioTech" : sidebar + dashboard +
catalogue + panneau de détails.

    python3 preview_modern.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from database.db_manager import DatabaseManager
from services.book_service import BookService
from chatbot.ai_assistant import AIAssistant
from ui.modern_shell import ModernShell, PAGE_BG


def main():
    DatabaseManager().initialize()

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("BiblioTech — Aperçu moderne")
    app.geometry("1340x800")
    app.minsize(1100, 680)
    app.configure(fg_color=PAGE_BG)

    # Utilisateur de démo (admin pour voir l'onglet Gestion)
    demo_user = {"id": 1, "username": "Hiba", "role": "admin"}

    shell = ModernShell(app, BookService(), user=demo_user,
                        on_logout=lambda: print("[LOGOUT] cliqué"),
                        ai_assistant=AIAssistant())
    shell.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == "__main__":
    main()
