"""
ui/chat_widget.py — Chatbot flottant (style Next.js)
-----------------------------------------------------
Bulle bleue flottante en bas à droite. Au clic, ouvre un panneau de
discussion BiblioBot (Google Gemini via AIAssistant) :
- En-tête blanc : avatar IA lavande, "BiblioBot", "Assistant IA • En ligne",
  statut "● Actif" vert
- Messages : avatar à côté des réponses du bot, bulles bleues pour l'utilisateur
- Bulle qui devient un "X" foncé quand le panneau est ouvert

L'appel à l'API se fait dans un thread pour ne pas bloquer l'interface.
"""

import threading
import customtkinter as ctk

from ui.icons import get_icon, get_fab
from ui.catalogue_frame import CARD_BG, BORDER, TITLE_CLR, SUBTLE_CLR, ACCENT

NAVY = "#0A1E5A"   # fond du panneau détails — pour fondre le halo de la bulle

USER_BUBBLE = "#2563EB"   # bulle utilisateur (bleu)
BOT_BUBBLE  = "#F3F4F6"   # bulle bot (gris clair)
BOT_TEXT    = "#111827"
AVATAR_BG   = "#EDE9FE"   # carré lavande de l'avatar IA
AVATAR_FG   = "#7C3AED"   # violet de l'icône sparkles
SEND_BG     = "#EEF2FF"   # fond clair du bouton envoyer
STATUS_GRN  = "#16A34A"
SEP         = "#EEF0F2"


class ChatWidget:
    """Bulle flottante + panneau de chat, posés en overlay sur le parent."""

    def __init__(self, parent, ai_assistant):
        self.parent = parent
        self.ai = ai_assistant
        self.open = False

        # Bulle flottante avec halo lumineux (image PIL).
        # fg_color = NAVY pour que le halo se fonde dans le panneau détails.
        self.bubble = ctk.CTkButton(
            parent, text="", image=get_fab("chat", circle=ACCENT, glow="#3B82F6"),
            width=100, height=100, corner_radius=0,
            fg_color=NAVY, hover=False,
            command=self.toggle,
        )
        self.bubble.place(relx=1.0, rely=1.0, x=-8, y=-8, anchor="se")

        # Panneau de chat (caché au départ)
        self.panel = ctk.CTkFrame(parent, width=380, height=520, corner_radius=18,
                                  fg_color=CARD_BG, border_width=1, border_color=BORDER)
        self._build_panel()

    # ── Construction du panneau ───────────────────────────────────────────────
    def _build_panel(self):
        self.panel.grid_propagate(False)
        self.panel.grid_columnconfigure(0, weight=1)
        self.panel.grid_rowconfigure(2, weight=1)

        # En-tête blanc
        header = ctk.CTkFrame(self.panel, fg_color=CARD_BG, corner_radius=0, height=68)
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=(2, 0))
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # Avatar IA (carré lavande + sparkles)
        ctk.CTkLabel(header, text="", image=get_icon("sparkles", AVATAR_FG, 20),
                     width=40, height=40, corner_radius=12, fg_color=AVATAR_BG,
                     ).grid(row=0, column=0, padx=(14, 10), pady=14)

        box = ctk.CTkFrame(header, fg_color="transparent")
        box.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(box, text="BiblioBot", font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TITLE_CLR).pack(anchor="w")
        ctk.CTkLabel(box, text="Assistant IA • En ligne",
                     font=ctk.CTkFont(size=11), text_color=SUBTLE_CLR).pack(anchor="w")

        ctk.CTkLabel(header, text="● Actif", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=STATUS_GRN).grid(row=0, column=2, padx=14)

        # Séparateur
        ctk.CTkFrame(self.panel, height=1, fg_color=SEP).grid(
            row=1, column=0, sticky="ew", padx=2)

        # Zone des messages
        self.messages = ctk.CTkScrollableFrame(self.panel, fg_color="#FAFAFA")
        self.messages.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)
        self.messages.grid_columnconfigure(0, weight=1)

        # Barre de saisie
        bar = ctk.CTkFrame(self.panel, fg_color="transparent", height=60)
        bar.grid(row=3, column=0, sticky="ew", padx=12, pady=12)
        bar.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(bar, height=42, corner_radius=12,
                                  placeholder_text="Ex: Le livre 102 est-il disponible ?",
                                  border_color=BORDER, fg_color="#F9FAFB")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self._send())

        self.send_btn = ctk.CTkButton(
            bar, text="", image=get_icon("send", ACCENT, 18), width=46, height=42,
            corner_radius=12, fg_color=SEND_BG, hover_color="#E0E7FF",
            command=self._send,
        )
        self.send_btn.grid(row=0, column=1)

        # Message d'accueil
        self._add_message(
            "Bonjour ! Je suis BiblioBot, l'assistant IA de la bibliothèque. "
            "Je peux vérifier la disponibilité des livres, vous donner des "
            "recommandations ou chercher un livre par son ID. "
            "Comment puis-je vous aider ?",
            sender="bot")

    # ── Ouverture / fermeture ─────────────────────────────────────────────────
    def toggle(self):
        if self.open:
            self.panel.place_forget()
            self.bubble.configure(image=get_fab("chat", circle=ACCENT, glow="#3B82F6"))
            self.open = False
        else:
            self.panel.place(relx=1.0, rely=1.0, x=-18, y=-110, anchor="se")
            self.panel.lift()
            self.bubble.lift()
            # La bulle devient un "X" foncé (halo discret)
            self.bubble.configure(image=get_fab("close", circle="#1F2937", glow="#1F2937"))
            self.open = True
            self.entry.focus()

    # ── Messages ──────────────────────────────────────────────────────────────
    def _add_message(self, text, sender="user"):
        row = ctk.CTkFrame(self.messages, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=2)

        if sender == "bot":
            ctk.CTkLabel(row, text="", image=get_icon("sparkles", AVATAR_FG, 14),
                         width=28, height=28, corner_radius=8, fg_color=AVATAR_BG,
                         ).pack(side="left", padx=(2, 6), anchor="n")
            bubble = ctk.CTkLabel(
                row, text=text, justify="left", wraplength=232,
                font=ctk.CTkFont(size=12), fg_color=BOT_BUBBLE, text_color=BOT_TEXT,
                corner_radius=12, anchor="w",
            )
            bubble.pack(side="left", ipadx=10, ipady=8)
        else:
            bubble = ctk.CTkLabel(
                row, text=text, justify="left", wraplength=240,
                font=ctk.CTkFont(size=12), fg_color=USER_BUBBLE, text_color="white",
                corner_radius=12, anchor="w",
            )
            bubble.pack(side="right", padx=2, ipadx=10, ipady=8)

        self.messages._parent_canvas.after(
            50, lambda: self.messages._parent_canvas.yview_moveto(1.0))
        return bubble

    def _send(self):
        question = self.entry.get().strip()
        if not question:
            return
        self.entry.delete(0, "end")
        self._add_message(question, sender="user")

        thinking = self._add_message("…", sender="bot")
        self.send_btn.configure(state="disabled")

        def worker():
            try:
                reply = self.ai.ask(question)
            except Exception as e:
                reply = f"⚠️ Erreur : {e}"
            self.panel.after(0, lambda: self._finish(thinking, reply))

        threading.Thread(target=worker, daemon=True).start()

    def _finish(self, thinking_bubble, reply):
        thinking_bubble.configure(text=reply)
        self.send_btn.configure(state="normal")
        self.messages._parent_canvas.after(
            50, lambda: self.messages._parent_canvas.yview_moveto(1.0))
