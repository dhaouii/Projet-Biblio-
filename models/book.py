"""
models/book.py — Modèle de données pour un Livre
--------------------------------------------------
Ce fichier définit la classe Book (le "modèle").
En programmation orientée objet, un modèle représente
une entité réelle — ici, un livre de bibliothèque.

Chaque attribut correspond exactement à une colonne
dans la table SQLite 'livres'.
"""


class Book:
    """
    Représente un livre dans la bibliothèque.
    
    Attributs :
        id          (int)  : Identifiant unique auto-incrémenté par SQLite
        titre       (str)  : Titre complet du livre
        auteur      (str)  : Nom de l'auteur (Prénom Nom)
        categorie   (str)  : Genre/catégorie (Roman, Science, Histoire...)
        annee       (int)  : Année de première publication
        quantite    (int)  : Nombre d'exemplaires disponibles physiquement
        statut      (str)  : État actuel — 'disponible', 'emprunté', 'réservé'
    """

    # Statuts possibles d'un livre — définis comme constantes de classe
    STATUT_DISPONIBLE = "disponible"
    STATUT_EMPRUNTE   = "emprunté"
    STATUT_RESERVE    = "réservé"

    def __init__(self, titre, auteur, categorie, annee, quantite=1,
                 statut="disponible", id=None, image_path=None):
        """
        Constructeur — crée un objet Book.
        
        Le paramètre 'id' est optionnel : il vaut None quand on crée
        un nouveau livre (SQLite assignera l'ID automatiquement),
        et il est renseigné quand on charge un livre depuis la base.
        """
        self.id       = id
        self.titre    = titre
        self.auteur   = auteur
        self.categorie = categorie
        self.annee    = annee
        self.quantite = quantite
        self.statut   = statut
        self.image_path = image_path   # chemin vers la couverture (optionnel)

    def to_tuple(self):
        """
        Convertit l'objet en tuple pour l'insertion SQLite.
        L'ordre correspond exactement aux colonnes de la requête INSERT.
        """
        return (self.titre, self.auteur, self.categorie,
                self.annee, self.quantite, self.statut, self.image_path)

    @classmethod
    def from_row(cls, row):
        """
        Méthode de classe — crée un Book à partir d'une ligne SQLite.
        
        'row' est un tuple retourné par sqlite3 :
        (id, titre, auteur, categorie, annee, quantite, statut)
        
        Le unpacking (*row[1:]) distribue les éléments restants
        dans les paramètres du constructeur dans l'ordre.
        """
        return cls(id=row[0], titre=row[1], auteur=row[2],
                   categorie=row[3], annee=row[4],
                   quantite=row[5], statut=row[6],
                   image_path=row[7] if len(row) > 7 else None)

    def __repr__(self):
        """Représentation lisible pour le debug."""
        return f"Book(id={self.id}, titre='{self.titre}', auteur='{self.auteur}')"
