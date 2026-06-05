"""
services/auth_service.py — Couche de service pour l'authentification
------------------------------------------------------------------
Gère l'inscription, la connexion et le hachage sécurisé des mots de passe.
"""

import hashlib
from database.db_manager import DatabaseManager

class AuthService:
    def __init__(self):
        self.db = DatabaseManager()

    def _hash_password(self, password: str) -> str:
        """
        Hache un mot de passe en utilisant SHA-256.
        En production, il faudrait ajouter un 'salt' (sel) ou utiliser bcrypt.
        Ici, SHA-256 est utilisé pour la simplicité et éviter des dépendances externes.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Inscrit un nouvel utilisateur.
        Le premier utilisateur devient automatiquement admin.
        Retourne (Succès, Message).
        """
        username = username.strip()
        if not username:
            return False, "Le nom d'utilisateur ne peut pas être vide."

        if len(password) < 4:
            return False, "Le mot de passe doit contenir au moins 4 caractères."

        password_hash = self._hash_password(password)

        is_first_user = self.db.get_user_count() == 0
        new_id = self.db.add_user(username, password_hash)

        if new_id is not None:
            if is_first_user:
                self.db.update_user_role(new_id, 'admin')
                return True, "Inscription réussie ! Vous êtes administrateur. Bienvenue !"
            else:
                return True, "Inscription réussie ! Vous pouvez maintenant vous connecter."
        else:
            return False, "Ce nom d'utilisateur est déjà pris."

    def login(self, username: str, password: str) -> tuple[bool, dict | str]:
        """
        Vérifie les identifiants d'un utilisateur.
        Retourne (Succès, dict{id, username, role} ou Message d'erreur).
        """
        username = username.strip()
        if not username or not password:
            return False, "Veuillez remplir tous les champs."

        user = self.db.get_user_by_username(username)

        if not user:
            return False, "Nom d'utilisateur ou mot de passe incorrect."

        password_hash = self._hash_password(password)

        if user['password_hash'] == password_hash:
            return True, {
                'id': user['id'],
                'username': user['username'],
                'role': user.get('role', 'user')
            }
        else:
            return False, "Nom d'utilisateur ou mot de passe incorrect."

    def is_admin(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est admin."""
        user = self.db.get_user_by_id(user_id)
        return user and user.get('role') == 'admin' if user else False

    def get_user_info(self, user_id: int) -> dict | None:
        """Récupère les infos d'un utilisateur."""
        return self.db.get_user_by_id(user_id)
