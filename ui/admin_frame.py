"""
ui/admin_frame.py — Panneau d'administration
---------------------------------------------
Interface pour gérer les utilisateurs, clés API, et logs d'activité.
Accessible uniquement aux administrateurs.
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from services.auth_service import AuthService


class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")

        self.current_user = current_user
        self.db = DatabaseManager()
        self.auth_service = AuthService()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self):
        """Construit l'interface admin avec onglets."""
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            main_frame,
            text="Panneau d'Administration",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        tabview = ctk.CTkTabview(main_frame, anchor="nw")
        tabview.grid(row=1, column=0, sticky="nsew")
        tabview.add("Utilisateurs")
        tabview.add("Clé API")
        tabview.add("Logs d'Activité")

        self._build_users_tab(tabview.tab("Utilisateurs"))
        self._build_api_tab(tabview.tab("Clé API"))
        self._build_logs_tab(tabview.tab("Logs d'Activité"))

    def _build_users_tab(self, parent):
        """Onglet gestion des utilisateurs."""
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Liste des Utilisateurs", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 15)
        )

        frame_list = ctk.CTkScrollableFrame(parent, height=250)
        frame_list.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        parent.grid_rowconfigure(1, weight=1)

        users = self.db.get_all_users()

        for i, user in enumerate(users):
            user_frame = ctk.CTkFrame(frame_list, fg_color=("gray90", "gray20"))
            user_frame.pack(fill="x", pady=5, padx=5)
            user_frame.grid_columnconfigure(1, weight=1)

            user_label = ctk.CTkLabel(
                user_frame,
                text=f"{user['username']} ({user['role'].upper()})",
                font=ctk.CTkFont(weight="bold")
            )
            user_label.grid(row=0, column=0, padx=10, pady=10)

            if user['id'] != self.current_user['id']:
                if user['role'] == 'user':
                    promote_btn = ctk.CTkButton(
                        user_frame,
                        text="→ Admin",
                        width=80,
                        height=30,
                        font=ctk.CTkFont(size=11),
                        command=lambda uid=user['id']: self._promote_user(uid, frame_list)
                    )
                    promote_btn.grid(row=0, column=1, padx=5, pady=10)
                else:
                    demote_btn = ctk.CTkButton(
                        user_frame,
                        text="← User",
                        width=80,
                        height=30,
                        font=ctk.CTkFont(size=11),
                        command=lambda uid=user['id']: self._demote_user(uid, frame_list)
                    )
                    demote_btn.grid(row=0, column=1, padx=5, pady=10)

                delete_btn = ctk.CTkButton(
                    user_frame,
                    text="Supprimer",
                    width=80,
                    height=30,
                    fg_color="#d9534f",
                    font=ctk.CTkFont(size=11),
                    command=lambda uid=user['id']: self._delete_user(uid, frame_list)
                )
                delete_btn.grid(row=0, column=2, padx=5, pady=10)

    def _promote_user(self, user_id: int, parent):
        """Promeut un utilisateur en admin."""
        self.db.update_user_role(user_id, 'admin')
        self.db.log_activity(
            self.current_user['id'],
            'promote_user',
            'user',
            user_id,
            f"Promotion de {user_id} en admin"
        )
        for widget in parent.winfo_children():
            widget.destroy()
        self._build_users_tab(parent.master)

    def _demote_user(self, user_id: int, parent):
        """Rétrograde un utilisateur en user normal."""
        self.db.update_user_role(user_id, 'user')
        self.db.log_activity(
            self.current_user['id'],
            'demote_user',
            'user',
            user_id,
            f"Rétrogradation de {user_id} en user"
        )
        for widget in parent.winfo_children():
            widget.destroy()
        self._build_users_tab(parent.master)

    def _delete_user(self, user_id: int, parent):
        """Supprime un utilisateur."""
        self.db.delete_user(user_id)
        self.db.log_activity(
            self.current_user['id'],
            'delete_user',
            'user',
            user_id,
            f"Suppression de l'utilisateur {user_id}"
        )
        for widget in parent.winfo_children():
            widget.destroy()
        self._build_users_tab(parent.master)

    def _build_api_tab(self, parent):
        """Onglet gestion de la clé API Gemini."""
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Clé API Google Gemini (Admin Shared)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 15)
        )

        ctk.CTkLabel(
            parent,
            text="Obtenez votre clé sur ai.google.dev",
            text_color="gray60"
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        entry = ctk.CTkEntry(parent, width=380, placeholder_text="AIza...", show="*")
        entry.grid(row=2, column=0, sticky="w", pady=(0, 15))

        current_key = self.db.get_api_key("gemini")
        if current_key:
            entry.insert(0, current_key)

        def save():
            key = entry.get().strip()
            if not key:
                ctk.CTkLabel(parent, text="La clé ne peut pas être vide.", text_color="#d9534f").grid(
                    row=3, column=0, sticky="w", pady=5
                )
                return
            self.db.set_api_key("gemini", key)
            self.db.log_activity(
                self.current_user['id'],
                'update_api_key',
                'api_key',
                None,
                "Mise à jour de la clé API Gemini"
            )
            ctk.CTkLabel(parent, text="✓ Clé API enregistrée avec succès.", text_color="#2d7a2d").grid(
                row=3, column=0, sticky="w", pady=5
            )

        ctk.CTkButton(parent, text="Enregistrer", command=save, width=200).grid(
            row=2, column=1, padx=10, pady=(0, 15)
        )

    def _build_logs_tab(self, parent):
        """Onglet logs d'activité."""
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(parent, text="Logs d'Activité Récente", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 15)
        )

        frame_logs = ctk.CTkScrollableFrame(parent, height=350)
        frame_logs.grid(row=1, column=0, sticky="nsew")
        parent.grid_rowconfigure(1, weight=1)

        logs = self.db.get_activity_logs(50)

        if not logs:
            ctk.CTkLabel(frame_logs, text="Aucun log d'activité", text_color="gray60").pack(pady=20)
        else:
            for log in logs:
                log_frame = ctk.CTkFrame(frame_logs, fg_color=("gray90", "gray20"))
                log_frame.pack(fill="x", pady=3, padx=5)

                username = log['username'] or "Système"
                timestamp = log['created_at'][:19]

                log_text = f"[{timestamp}] {username} — {log['action']}"
                if log['details']:
                    log_text += f" — {log['details']}"

                ctk.CTkLabel(
                    log_frame,
                    text=log_text,
                    text_color="gray70",
                    font=ctk.CTkFont(size=11)
                ).pack(padx=10, pady=5, anchor="w")
