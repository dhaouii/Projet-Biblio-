"""
database/db_manager.py — Gestionnaire de la base de données SQLite
-------------------------------------------------------------------
Ce fichier gère toute la communication avec SQLite.
C'est la couche "persistance" de l'application :
elle traduit les objets Python en données SQL et vice-versa.

Pourquoi SQLite ?
- Intégré à Python (module sqlite3, aucune installation)
- Fichier unique (library.db) — facile à partager
- Parfait pour un projet local sans serveur
"""

import sqlite3
import os
from models.book import Book


# Chemin absolu vers le fichier de base de données
# __file__ = chemin de ce script → on remonte d'un niveau pour la racine
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library.db")


class DatabaseManager:
    """
    Classe responsable de toutes les opérations SQLite.
    
    Chaque méthode correspond à une opération CRUD :
    Create → add_book()
    Read   → get_all_books(), search_books()
    Update → update_book()
    Delete → delete_book()
    """

    def __init__(self):
        """Stocke juste le chemin — la connexion s'ouvre à chaque opération."""
        self.db_path = DB_PATH

    def _connect(self):
        """
        Ouvre une connexion SQLite.
        
        row_factory = sqlite3.Row permet d'accéder aux colonnes
        par nom (row['titre']) en plus de l'index (row[1]).
        On utilise des tuples simples ici pour la clarté.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        """
        Crée la table 'livres' si elle n'existe pas encore.
        
        'IF NOT EXISTS' est crucial : sans ça, chaque démarrage
        de l'app effacerait et recréérait la table.
        
        'INTEGER PRIMARY KEY AUTOINCREMENT' = SQLite génère
        automatiquement un ID unique pour chaque nouveau livre.
        """
        sql_create = """
        CREATE TABLE IF NOT EXISTS livres (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            titre             TEXT    NOT NULL,
            auteur            TEXT    NOT NULL,
            categorie         TEXT    NOT NULL,
            annee_publication INTEGER NOT NULL,
            quantite          INTEGER DEFAULT 1,
            statut            TEXT    DEFAULT 'disponible'
        );
        """

        # Données de démonstration — insérées seulement si la table est vide
        sql_demo_data = """
        INSERT INTO livres (titre, auteur, categorie, annee_publication, quantite, statut)
        SELECT * FROM (VALUES
            ('Les Misérables',         'Victor Hugo',             'Roman',       1862, 3, 'disponible'),
            ('Notre-Dame de Paris',    'Victor Hugo',             'Roman',       1831, 2, 'disponible'),
            ('Le Petit Prince',        'Antoine de Saint-Exupéry','Jeunesse',    1943, 5, 'disponible'),
            ('L''Étranger',            'Albert Camus',            'Roman',       1942, 2, 'emprunté'),
            ('Candide',                'Voltaire',                'Philosophie', 1759, 1, 'disponible'),
            ('Germinal',               'Émile Zola',              'Roman',       1885, 2, 'réservé'),
            ('Madame Bovary',          'Gustave Flaubert',        'Roman',       1857, 1, 'disponible'),
            ('Le Rouge et le Noir',    'Stendhal',                'Roman',       1830, 2, 'disponible'),
            ('Bel-Ami',                'Guy de Maupassant',       'Roman',       1885, 1, 'emprunté'),
            ('Python pour tous',       'Charles Severance',       'Informatique',2016, 3, 'disponible')
        )
        WHERE NOT EXISTS (SELECT 1 FROM livres LIMIT 1);
        """

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(sql_create)
        cursor.executescript(sql_demo_data)
        conn.commit()
        conn.close()

    # ─── CREATE ────────────────────────────────────────────────────────────────

    def add_book(self, book: Book) -> int:
        """
        Insère un nouveau livre dans la base.
        
        '?' sont des placeholders paramétrés — ils protègent contre
        les injections SQL (si un titre contient des guillemets, etc.)
        
        lastrowid retourne l'ID auto-généré par SQLite.
        """
        sql = """
        INSERT INTO livres (titre, auteur, categorie, annee_publication, quantite, statut)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(sql, book.to_tuple())
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    # ─── READ ─────────────────────────────────────────────────────────────────

    def get_all_books(self) -> list[Book]:
        """
        Retourne tous les livres triés par titre.
        
        fetchall() retourne une liste de tuples.
        List comprehension → on convertit chaque tuple en objet Book.
        """
        sql = "SELECT * FROM livres ORDER BY titre"
        conn = self._connect()
        rows = conn.execute(sql).fetchall()
        conn.close()
        return [Book.from_row(tuple(row)) for row in rows]

    def get_book_by_id(self, book_id: int) -> Book | None:
        """
        Recherche un livre par son ID.
        Returns None si aucun livre ne correspond.
        """
        sql = "SELECT * FROM livres WHERE id = ?"
        conn = self._connect()
        row = conn.execute(sql, (book_id,)).fetchone()
        conn.close()
        return Book.from_row(tuple(row)) if row else None

    def search_books(self, query: str) -> list[Book]:
        """
        Recherche full-text dans titre, auteur et catégorie.
        
        LIKE '%?%' avec LOWER() = recherche insensible à la casse.
        Les % autour du terme = le terme peut apparaître n'importe où.
        """
        term = f"%{query.lower()}%"
        sql = """
        SELECT * FROM livres
        WHERE LOWER(titre) LIKE ?
           OR LOWER(auteur) LIKE ?
           OR LOWER(categorie) LIKE ?
        ORDER BY titre
        """
        conn = self._connect()
        rows = conn.execute(sql, (term, term, term)).fetchall()
        conn.close()
        return [Book.from_row(tuple(row)) for row in rows]

    def get_books_by_category(self, categorie: str) -> list[Book]:
        """Filtre par catégorie exacte."""
        sql = "SELECT * FROM livres WHERE LOWER(categorie) = LOWER(?)"
        conn = self._connect()
        rows = conn.execute(sql, (categorie,)).fetchall()
        conn.close()
        return [Book.from_row(tuple(row)) for row in rows]

    def get_books_by_status(self, statut: str) -> list[Book]:
        """Filtre par statut ('disponible', 'emprunté', 'réservé')."""
        sql = "SELECT * FROM livres WHERE statut = ?"
        conn = self._connect()
        rows = conn.execute(sql, (statut,)).fetchall()
        conn.close()
        return [Book.from_row(tuple(row)) for row in rows]

    def get_stats(self) -> dict:
        """
        Retourne des statistiques agrégées pour le tableau de bord.
        COUNT(*) = nombre total de lignes
        SUM()    = somme d'une colonne numérique
        """
        sql = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN statut = 'disponible' THEN 1 ELSE 0 END) as disponibles,
            SUM(CASE WHEN statut = 'emprunté'   THEN 1 ELSE 0 END) as empruntes,
            SUM(CASE WHEN statut = 'réservé'    THEN 1 ELSE 0 END) as reserves,
            COUNT(DISTINCT categorie) as categories
        FROM livres
        """
        conn = self._connect()
        row = dict(conn.execute(sql).fetchone())
        conn.close()
        return row

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    def update_book(self, book: Book) -> bool:
        """
        Met à jour un livre existant.
        WHERE id = ? assure qu'on modifie le bon enregistrement.
        rowcount = nombre de lignes modifiées (0 si l'ID n'existe pas).
        """
        sql = """
        UPDATE livres
        SET titre = ?, auteur = ?, categorie = ?,
            annee_publication = ?, quantite = ?, statut = ?
        WHERE id = ?
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(sql, (*book.to_tuple(), book.id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    # ─── DELETE ───────────────────────────────────────────────────────────────

    def delete_book(self, book_id: int) -> bool:
        """
        Supprime un livre par son ID.
        Retourne True si la suppression a réussi.
        """
        sql = "DELETE FROM livres WHERE id = ?"
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(sql, (book_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def get_all_categories(self) -> list[str]:
        """Retourne la liste unique des catégories présentes dans la base."""
        sql = "SELECT DISTINCT categorie FROM livres ORDER BY categorie"
        conn = self._connect()
        rows = conn.execute(sql).fetchall()
        conn.close()
        return [row[0] for row in rows]
