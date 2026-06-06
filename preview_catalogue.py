"""
preview_catalogue.py — Aperçu standalone de l'écran Catalogue
--------------------------------------------------------------
Lance UNIQUEMENT le nouvel écran Catalogue (style "BiblioTech")
pour valider le design avant de redessiner le reste de l'app.

    python3 preview_catalogue.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from database.db_manager import DatabaseManager
from services.book_service import BookService
from ui.catalogue_frame import CatalogueFrame, PAGE_BG


def main():
    DatabaseManager().initialize()

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Aperçu — Catalogue")
    app.geometry("980x720")
    app.configure(fg_color=PAGE_BG)

    catalogue = CatalogueFrame(app, BookService())
    catalogue.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == "__main__":
    main()
