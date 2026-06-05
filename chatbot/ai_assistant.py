"""
chatbot/ai_assistant.py — Moteur du Chatbot IA
------------------------------------------------
Ce fichier gère toute la communication avec l'API Google Gemini.
"""

import os
import google.generativeai as genai
from services.book_service import BookService


class AIAssistant:
    """
    Chatbot alimenté par Google Gemini.
    Il répond aux questions sur la bibliothèque en consultant
    les données SQLite en temps réel.
    """

    # Prompt système — définit le rôle et le comportement du chatbot
    SYSTEM_PROMPT = """Tu es l'assistant intelligent de la Bibliothèque Universitaire.
Tu t'appelles "BiblioBot" et tu aides les étudiants et lecteurs.

Règles importantes :
- Réponds UNIQUEMENT en français
- Utilise les données réelles fournies dans le contexte
- Sois naturel, chaleureux et utile
- Si un livre est emprunté, dis-le clairement
- Pour les recommandations, base-toi sur les catégories et statuts disponibles
- N'invente JAMAIS de données qui ne sont pas dans le contexte fourni
- Sois concis mais complet dans tes réponses
- Utilise des emojis avec parcimonie pour rendre les réponses plus lisibles

Tu peux répondre à :
- La disponibilité d'un livre spécifique
- La recherche par auteur ou catégorie  
- Les recommandations selon le goût du lecteur
- L'existence d'un livre par ID ou titre
- Les statistiques générales de la bibliothèque
"""

    def __init__(self, api_key: str = None):
        """Initialise le chatbot en chargeant la clé API de la base de données."""
        from database.db_manager import DatabaseManager

        self.db = DatabaseManager()

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self.db.get_api_key("gemini")
            if not self.api_key:
                self.api_key = "AIzaSyCpBASEss_v8gD4AGMLt3UWiw5B60ylvCo"

        self.book_service = BookService()
        self.model = None
        self.is_configured = False

        self._configure()

    def _configure(self):
        """Configure l'API Gemini avec la clé forcée."""
        try:
            genai.configure(api_key=self.api_key)
            # Utilisation du modèle stable et rapide de Google
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.is_configured = True
            print("[CHATBOT] Connexion réussie à Google Gemini.")
        except Exception as e:
            print(f"[CHATBOT] Erreur de configuration Gemini: {e}")
            self.is_configured = False

    def set_api_key(self, api_key: str):
        """Met à jour la clé API."""
        if api_key and api_key.strip():
            self.api_key = api_key.strip()
            self._configure()

    def ask(self, question: str) -> str:
        """Pose une question au chatbot Gemini et gère la connexion en temps réel."""
        if not question.strip():
            return "Je n'ai pas reçu de question. Pouvez-vous reformuler ?"

        if not self.is_configured or self.model is None:
            self._configure()

        # Récupération des données SQLite fraîches de la bibliothèque
        context = self.book_service.get_context_for_chatbot()

        # Construction du prompt final (Prompt Engineering)
        full_prompt = f"""
{self.SYSTEM_PROMPT}

=== DONNÉES ACTUELLES DE LA BIBLIOTHÈQUE ===
{context}
===========================================

Question du lecteur : {question}

Réponds en te basant UNIQUEMENT sur les données ci-dessus.
"""

        try:
            # Appel direct aux serveurs de Google Gemini
            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            error_msg = str(e)
            # Détection et traitement des erreurs classiques d'API
            if "API_KEY_INVALID" in error_msg or "400" in error_msg:
                return "❌ Clé API invalide ou refusée par Google. Vérifiez vos restrictions d'API."
            elif "quota" in error_msg.lower():
                return "⚠️ Quota API gratuit dépassé. Réessayez dans une minute."
            else:
                # En cas de coupure réseau ou problème imprévu, bascule sur le secours local
                return self._offline_response(question)

    def _offline_response(self, question: str) -> str:
        """Mode dégradé local si le réseau ou l'API échoue."""
        q = question.lower()
        books = self.book_service.get_all_books()
        stats = self.book_service.get_stats()

        # Recherche par auteur locale
        for book in books:
            if book.auteur.lower() in q:
                same_author = [b for b in books if b.auteur == book.auteur]
                result = f"📚 Livres de {book.auteur} dans notre catalogue :\n"
                for b in same_author:
                    emoji = "✅" if b.statut == "disponible" else "📤"
                    result += f"  {emoji} '{b.titre}' ({b.annee}) — {b.statut}\n"
                return result

        # Recherche de disponibilité locale
        if any(w in q for w in ["disponible", "disponibles", "peut-on emprunter"]):
            available = [b for b in books if b.statut == "disponible"]
            result = f"✅ {len(available)} livre(s) disponible(s) :\n"
            for b in available[:8]:
                result += f"  • '{b.titre}' — {b.auteur}\n"
            return result

        # Statistiques locales
        if any(w in q for w in ["combien", "total", "statistique", "stats"]):
            return (f"📊 Statistiques de la bibliothèque :\n"
                    f"  • Total : {stats['total']} livres\n"
                    f"  • Disponibles : {stats['disponibles']}\n"
                    f"  • Empruntés : {stats['empruntes']}\n"
                    f"  • Réservés : {stats['reserves']}\n"
                    f"  • Catégories : {stats['categories']}")

        return (f"💡 Initialisation de BiblioBot ou problème de réseau.\n"
                f"La bibliothèque contient actuellement {stats['total']} livres dont {stats['disponibles']} disponibles.")