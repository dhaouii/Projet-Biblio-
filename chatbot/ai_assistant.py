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

        # Priorité : clé passée explicitement → base de données → variable
        # d'environnement. AUCUNE clé n'est codée en dur (sécurité / GitHub).
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self.db.get_api_key("gemini") or os.environ.get("GEMINI_API_KEY")

        self.book_service = BookService()
        self.model = None
        self.is_configured = False

        self._configure()

    # Modèle unique fiable : alias "latest" qui pointe vers le modèle flash
    # courant et dispose d'un quota gratuit (les variantes 2.0 figées sont
    # souvent sans quota gratuit → 429).
    MODEL = "gemini-flash-latest"

    def _configure(self):
        """Configure l'API Gemini avec la clé courante."""
        if not self.api_key:
            print("[CHATBOT] Aucune clé API → mode hors-ligne. "
                  "Ajoutez-en une via « Clé API Gemini » ou la variable GEMINI_API_KEY.")
            self.is_configured = False
            return
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.MODEL)
            self.is_configured = True
            print(f"[CHATBOT] Connexion réussie à Google Gemini ({self.MODEL}).")
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
            # Appel direct à Gemini avec le modèle unique configuré
            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            print(f"[CHATBOT] Erreur Gemini ({self.MODEL}) : {e}")
            error_msg = str(e)
            low = error_msg.lower()
            # Détection et traitement des erreurs classiques d'API
            if "leaked" in low or "permission_denied" in low:
                return ("🔒 Cette clé API a été bloquée par Google (signalée comme « fuitée »).\n"
                        "Créez une NOUVELLE clé sur ai.google.dev, puis enregistrez-la "
                        "via le bouton « Clé API Gemini ».")
            elif "not found" in low or "404" in low:
                return ("❌ Modèle Gemini introuvable (nom obsolète).\n"
                        "Mettez à jour le modèle dans le code (ex: gemini-2.0-flash).")
            elif "api_key_invalid" in low or "400" in low:
                return "❌ Clé API invalide ou refusée par Google. Vérifiez votre clé."
            elif "quota" in low or "resource_exhausted" in low or "429" in low:
                return ("⚠️ Limite Gemini atteinte (quota gratuit).\n"
                        "• Soit la limite par minute → attends ~60 s et réessaie.\n"
                        "• Soit le quota journalier est épuisé → réessaie demain "
                        "ou active la facturation sur ta clé.")
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