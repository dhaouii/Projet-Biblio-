"""
ui/chat_frame.py — Interface du Chatbot IA
------------------------------------------
Cette frame affiche une interface de chat classique :
- Historique des messages (scrollable)
- Champ de saisie + bouton Envoyer
- Indicateur de chargement pendant l'appel API
"""

import customtkinter as ctk
import threading
from chatbot.ai_assistant import AIAssistant


class ChatFrame(ctk.CTkFrame):
    """
    Interface de chat avec le chatbot IA.
    
    Important : les appels API Gemini sont faits dans un thread séparé
    pour ne pas bloquer l'interface pendant l'attente de la réponse.
    """

    def __init__(self, parent, ai_assistant: AIAssistant):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.ai_assistant = ai_assistant
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── En-tête ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(header, text="🤖 Assistant IA",
                     font=ctk.CTkFont(size=24, weight="bold")
                     ).pack(side="left")

        # Indicateur de statut API
        self.status_label = ctk.CTkLabel(
            header,
            text="● Sans clé API (mode hors-ligne)" if not self.ai_assistant.is_configured
                 else "● Connecté à Gemini",
            text_color="gray" if not self.ai_assistant.is_configured else "#34C759",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right")

        # ── Zone des messages ─────────────────────────────────────
        self.chat_display = ctk.CTkTextbox(
            self,
            state="disabled",  # Lecture seule — l'utilisateur ne peut pas écrire directement
            wrap="word",
            font=ctk.CTkFont(size=13),
            corner_radius=10
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)

        # ── Zone de saisie ────────────────────────────────────────
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 20))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Posez une question sur la bibliothèque...",
            height=45,
            font=ctk.CTkFont(size=13)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Entrée = touche Enter pour envoyer
        self.input_entry.bind("<Return>", lambda e: self._send_message())

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Envoyer",
            width=100,
            height=45,
            corner_radius=10,
            command=self._send_message
        )
        self.send_btn.grid(row=0, column=1)

        # ── Suggestions de questions ──────────────────────────────
        suggestions_frame = ctk.CTkFrame(self, fg_color="transparent")
        suggestions_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(suggestions_frame, text="Exemples :",
                     text_color="gray60").pack(side="left", padx=(0, 10))

        suggestions = [
            "Livres disponibles ?",
            "Livres de Victor Hugo",
            "Propose un roman",
        ]
        for suggestion in suggestions:
            ctk.CTkButton(
                suggestions_frame,
                text=suggestion,
                height=28,
                corner_radius=14,
                fg_color=("#f0f0f5", "gray25"),
                border_width=0,
                text_color=("gray30", "gray70"),
                hover_color=("#e0e0ea", "gray35"),
                font=ctk.CTkFont(size=11),
                command=lambda s=suggestion: self._use_suggestion(s)
            ).pack(side="left", padx=3)

        # Message de bienvenue
        self._add_message("bot", "👋 Bonjour ! Je suis BiblioBot, votre assistant bibliothécaire intelligent.\n"
                                  "Posez-moi des questions sur les livres disponibles, les auteurs, ou demandez des recommandations !")

    def _send_message(self):
        """
        Envoie un message au chatbot.
        
        Le traitement se fait dans un thread séparé (threading.Thread)
        pour ne pas bloquer l'interface pendant l'appel API.
        Si on ne le faisait pas, l'interface "freeze" pendant 1-3 secondes.
        """
        question = self.input_entry.get().strip()
        if not question:
            return

        # Affiche la question de l'utilisateur
        self._add_message("user", question)
        self.input_entry.delete(0, "end")

        # Désactive le bouton pendant le traitement
        self.send_btn.configure(state="disabled", text="...")

        # Lancement dans un thread background
        thread = threading.Thread(target=self._process_in_thread, args=(question,))
        thread.daemon = True  # Se termine quand l'app se ferme
        thread.start()

    def _process_in_thread(self, question: str):
        """
        Appel API dans le thread background.
        
        after(0, callback) = planifie l'exécution dans le thread principal
        Tkinter n'est pas thread-safe : toute modification de l'UI
        doit se faire depuis le thread principal.
        """
        response = self.ai_assistant.ask(question)
        # Retour dans le thread principal pour mettre à jour l'UI
        self.after(0, self._on_response, response)

    def _on_response(self, response: str):
        """Affiche la réponse et réactive le bouton d'envoi."""
        self._add_message("bot", response)
        self.send_btn.configure(state="normal", text="Envoyer")

    def _add_message(self, sender: str, text: str):
        """
        Ajoute un message dans la zone d'affichage.
        
        state="normal" → on déverrouille temporairement pour écrire
        state="disabled" → on reverrouille après → lecture seule
        """
        self.chat_display.configure(state="normal")

        if sender == "user":
            self.chat_display.insert("end", "\n🧑 Vous\n", "user_header")
            self.chat_display.insert("end", text + "\n", "user_text")
        else:
            self.chat_display.insert("end", "\n🤖 BiblioBot\n", "bot_header")
            self.chat_display.insert("end", text + "\n", "bot_text")

        self.chat_display.insert("end", "─" * 50 + "\n", "separator")
        self.chat_display.configure(state="disabled")

        # Scroll automatique vers le bas
        self.chat_display.see("end")

    def _use_suggestion(self, suggestion: str):
        """Remplit le champ de saisie avec la suggestion cliquée."""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, suggestion)
        self.input_entry.focus()

    def refresh(self):
        """Met à jour l'indicateur de statut API."""
        if self.ai_assistant.is_configured:
            self.status_label.configure(text="● Connecté à Gemini",
                                         text_color="#34C759")
        else:
            self.status_label.configure(text="● Mode hors-ligne",
                                         text_color="gray")
