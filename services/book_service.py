"""
services/book_service.py — Couche de service (logique métier)
--------------------------------------------------------------
Ce fichier est la couche intermédiaire entre l'UI et la base de données.

Pourquoi cette couche ?
- L'UI ne doit pas faire de SQL directement
- La validation des données se fait ici, pas dans l'interface
- Si on change de base de données (SQLite → MySQL), seule cette
  couche change, pas l'interface utilisateur

Pattern utilisé : Service Layer (couche de service)
"""

from database.db_manager import DatabaseManager
from models.book import Book


class BookService:
    """
    Orchestre les opérations sur les livres.
    Valide les données avant de les envoyer à la base.
    """

    def __init__(self):
        """Instancie le gestionnaire de base de données."""
        self.db = DatabaseManager()

    def add_book(self, titre: str, auteur: str, categorie: str,
                 annee: int, quantite: int, statut: str) -> tuple[bool, str]:
        """
        Valide et ajoute un nouveau livre.
        
        Retourne un tuple (succès: bool, message: str).
        Ce pattern permet à l'UI d'afficher le bon message
        sans connaître les détails de la validation.
        """
        # ── Validation ──────────────────────────────────────────
        if not titre.strip():
            return False, "Le titre ne peut pas être vide."

        if not auteur.strip():
            return False, "L'auteur ne peut pas être vide."

        if not categorie.strip():
            return False, "La catégorie est obligatoire."

        try:
            annee = int(annee)
            if annee < 1000 or annee > 2030:
                return False, "L'année doit être entre 1000 et 2030."
        except (ValueError, TypeError):
            return False, "L'année doit être un nombre entier valide."

        try:
            quantite = int(quantite)
            if quantite < 0:
                return False, "La quantité ne peut pas être négative."
        except (ValueError, TypeError):
            return False, "La quantité doit être un nombre entier."

        valid_statuts = [Book.STATUT_DISPONIBLE, Book.STATUT_EMPRUNTE, Book.STATUT_RESERVE]
        if statut not in valid_statuts:
            return False, f"Statut invalide. Choisir parmi : {', '.join(valid_statuts)}"

        # ── Insertion ───────────────────────────────────────────
        book = Book(titre=titre.strip(), auteur=auteur.strip(),
                    categorie=categorie.strip(), annee=annee,
                    quantite=quantite, statut=statut)
        new_id = self.db.add_book(book)
        return True, f"Livre ajouté avec succès (ID: {new_id})."

    def update_book(self, id: int, titre: str, auteur: str, categorie: str,
                    annee: int, quantite: int, statut: str) -> tuple[bool, str]:
        """Valide et met à jour un livre existant."""
        # Même validation que add_book
        if not titre.strip():
            return False, "Le titre ne peut pas être vide."
        try:
            annee = int(annee)
            quantite = int(quantite)
        except (ValueError, TypeError):
            return False, "Année et quantité doivent être des nombres."

        book = Book(id=id, titre=titre.strip(), auteur=auteur.strip(),
                    categorie=categorie.strip(), annee=annee,
                    quantite=quantite, statut=statut)
        success = self.db.update_book(book)

        if success:
            return True, "Livre mis à jour avec succès."
        return False, f"Aucun livre trouvé avec l'ID {id}."

    def delete_book(self, book_id: int) -> tuple[bool, str]:
        """Supprime un livre après vérification de son existence."""
        book = self.db.get_book_by_id(book_id)
        if not book:
            return False, f"Livre ID {book_id} introuvable."

        self.db.delete_book(book_id)
        return True, f"Le livre '{book.titre}' a été supprimé."

    def get_all_books(self) -> list[Book]:
        return self.db.get_all_books()

    def search_books(self, query: str) -> list[Book]:
        if not query.strip():
            return self.get_all_books()
        return self.db.search_books(query.strip())

    def get_books_by_category(self, categorie: str) -> list[Book]:
        return self.db.get_books_by_category(categorie)

    def get_stats(self) -> dict:
        return self.db.get_stats()

    def get_all_categories(self) -> list[str]:
        return self.db.get_all_categories()

    def get_context_for_chatbot(self) -> str:
        """
        Génère un résumé textuel de la bibliothèque pour le chatbot.
        
        Le chatbot IA (Gemini) a besoin de connaître les données
        de la bibliothèque. On lui fournit sous forme de texte structuré.
        
        Cette approche s'appelle "RAG simplifié" (Retrieval Augmented Generation) :
        on injecte les données dans le prompt plutôt que d'entraîner le modèle.
        """
        books = self.get_all_books()
        stats = self.get_stats()

        lines = [
            f"BIBLIOTHÈQUE — {stats['total']} livres au total",
            f"Disponibles: {stats['disponibles']} | Empruntés: {stats['empruntes']} | Réservés: {stats['reserves']}",
            "",
            "CATALOGUE COMPLET :"
        ]

        for book in books:
            lines.append(
                f"- ID {book.id} | '{book.titre}' par {book.auteur} "
                f"| {book.categorie} | {book.annee} "
                f"| {book.quantite} ex. | STATUT: {book.statut.upper()}"
            )

        return "\n".join(lines)
