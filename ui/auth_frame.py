"""
ui/auth_frame.py — Écran de connexion et d'inscription
------------------------------------------------------
Interface minimaliste de style Apple pour l'authentification.
"""

import customtkinter as ctk
from services.auth_service import AuthService
from ui.icons import get_logo

class AuthFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")

        self.auth_service = AuthService()
        self.on_login_success = on_login_success
        self.current_user = None
        
        # Centrage du contenu
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_login_ui()

    def _build_login_ui(self):
        """Construit l'interface de connexion."""
        # Nettoyer la vue si on vient de l'inscription
        for widget in self.winfo_children():
            widget.destroy()

        # Cadre central avec effet "carte" macOS
        # Un gris très léger en mode clair, et gris sombre en mode sombre
        card = ctk.CTkFrame(self, width=380, corner_radius=15)
        card.grid(row=0, column=0, pady=50)
        card.grid_columnconfigure(0, weight=1)
        
        # On empêche le cadre de rétrécir à la taille de son contenu
        card.grid_propagate(False)
        card.configure(height=490)

        # Logo de l'app : carré dégradé bleu + livre au trait
        ctk.CTkLabel(card, text="", image=get_logo(68),
                     ).pack(pady=(40, 14))
        ctk.CTkLabel(card, text="BiblioTech", font=ctk.CTkFont(size=28, weight="bold"), text_color="#2563EB").pack(pady=(0, 2))
        ctk.CTkLabel(card, text="Bienvenue", font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(card, text="Connectez-vous à votre bibliothèque", text_color="gray50", font=ctk.CTkFont(size=12)).pack(pady=(0, 30))

        # Champs
        self.username_entry = ctk.CTkEntry(card, placeholder_text="Nom d'utilisateur", width=280, height=40, corner_radius=8)
        self.username_entry.pack(pady=(0, 15))

        self.password_entry = ctk.CTkEntry(card, placeholder_text="Mot de passe", show="*", width=280, height=40, corner_radius=8)
        self.password_entry.pack(pady=(0, 5))
        
        self.error_label = ctk.CTkLabel(card, text="", text_color="#d9534f", font=ctk.CTkFont(size=12))
        self.error_label.pack(pady=(0, 15))

        # Bouton principal (Bleu Apple)
        ctk.CTkButton(card, text="Se connecter", command=self._handle_login, width=280, height=40, corner_radius=8, font=ctk.CTkFont(weight="bold")).pack(pady=(0, 20))

        # Lien vers inscription
        link_frame = ctk.CTkFrame(card, fg_color="transparent")
        link_frame.pack()
        
        ctk.CTkLabel(link_frame, text="Nouveau ici ?", text_color="gray50", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        register_btn = ctk.CTkLabel(link_frame, text="Créer un compte", text_color="#0A84FF", cursor="hand2", font=ctk.CTkFont(size=12, weight="bold"))
        register_btn.pack(side="left")
        register_btn.bind("<Button-1>", lambda e: self._build_register_ui())

    def _build_register_ui(self):
        """Construit l'interface d'inscription."""
        for widget in self.winfo_children():
            widget.destroy()

        card = ctk.CTkFrame(self, width=380, corner_radius=15)
        card.grid(row=0, column=0, pady=50)
        card.grid_columnconfigure(0, weight=1)
        card.grid_propagate(False)
        card.configure(height=490)

        # Logo de l'app : carré dégradé bleu + livre au trait
        ctk.CTkLabel(card, text="", image=get_logo(68),
                     ).pack(pady=(40, 14))
        ctk.CTkLabel(card, text="BiblioTech", font=ctk.CTkFont(size=28, weight="bold"), text_color="#2563EB").pack(pady=(0, 2))
        ctk.CTkLabel(card, text="Inscription", font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(card, text="Créez votre compte lecteur", text_color="gray50", font=ctk.CTkFont(size=12)).pack(pady=(0, 30))

        self.reg_username_entry = ctk.CTkEntry(card, placeholder_text="Nom d'utilisateur", width=280, height=40, corner_radius=8)
        self.reg_username_entry.pack(pady=(0, 15))

        self.reg_password_entry = ctk.CTkEntry(card, placeholder_text="Mot de passe", show="*", width=280, height=40, corner_radius=8)
        self.reg_password_entry.pack(pady=(0, 5))
        
        self.reg_error_label = ctk.CTkLabel(card, text="", text_color="#d9534f", font=ctk.CTkFont(size=12))
        self.reg_error_label.pack(pady=(0, 15))

        ctk.CTkButton(card, text="S'inscrire", command=self._handle_register, width=280, height=40, corner_radius=8, font=ctk.CTkFont(weight="bold")).pack(pady=(0, 20))

        link_frame = ctk.CTkFrame(card, fg_color="transparent")
        link_frame.pack()
        
        ctk.CTkLabel(link_frame, text="Déjà un compte ?", text_color="gray50", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        login_btn = ctk.CTkLabel(link_frame, text="Se connecter", text_color="#0A84FF", cursor="hand2", font=ctk.CTkFont(size=12, weight="bold"))
        login_btn.pack(side="left")
        login_btn.bind("<Button-1>", lambda e: self._build_login_ui())

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        success, result = self.auth_service.login(username, password)
        if success:
            self.current_user = result
            self.on_login_success(result)
        else:
            self.error_label.configure(text=result, text_color="#d9534f")

    def _handle_register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        
        success, message = self.auth_service.register(username, password)
        if success:
            self.reg_error_label.configure(text=message, text_color="#2d7a2d") # Vert succès
            # Revenir à la page de login après un court délai
            self.after(2000, self._build_login_ui)
        else:
            self.reg_error_label.configure(text=message, text_color="#d9534f")
