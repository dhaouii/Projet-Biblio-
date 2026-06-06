"""
main.py — Point d'entrée principal de l'application
-----------------------------------------------------
Ce fichier initialise la base de données et lance l'interface graphique.
Il sert de chef d'orchestre : il importe tous les modules nécessaires
et s'assure que tout est prêt avant d'ouvrir la fenêtre.
"""

import sys
import os

# On ajoute le dossier racine au chemin Python pour que les imports fonctionnent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from ui.modern_app import ModernApp


def main():
    """
    Fonction principale — appelée au démarrage.
    1. Crée la base de données SQLite si elle n'existe pas encore
    2. Lance l'interface graphique moderne (login → dashboard BiblioTech)
    """
    # Étape 1 : Initialisation de la base de données
    # Si library.db n'existe pas, elle sera créée avec toutes les tables
    db = DatabaseManager()
    db.initialize()

    # Étape 2 : Lancement de l'interface graphique moderne
    # (ancienne interface toujours disponible via ui.app.BibliothequeApp)
    app = ModernApp()
    app.mainloop()  # Boucle d'événements Tkinter — l'app reste ouverte jusqu'à fermeture


if __name__ == "__main__":
    main()
