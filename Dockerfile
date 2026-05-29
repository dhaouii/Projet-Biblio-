# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — Bibliothèque Intelligente avec Chatbot IA
# Compatible macOS + Docker Desktop
# ─────────────────────────────────────────────────────────────────────────────
#
# POURQUOI CE DOCKERFILE ?
# Sur Mac, CustomTkinter (interface graphique) nécessite un affichage X11.
# Docker ne peut pas afficher une fenêtre directement — il faut XQuartz.
#
# ÉTAPES REQUISES SUR MAC AVANT DE LANCER :
# 1. Installer XQuartz : brew install --cask xquartz
# 2. Ouvrir XQuartz et activer "Allow connections from network clients"
#    (Préférences → Sécurité)
# 3. Redémarrer la session
# 4. Lancer : xhost + 127.0.0.1
# ─────────────────────────────────────────────────────────────────────────────

# Image de base : Python 3.11 sur Debian slim (légère)
FROM python:3.11-slim

# Métadonnées du projet
LABEL maintainer="Etudiant iTeam University"
LABEL description="Bibliothèque Intelligente avec Chatbot IA"

# ── Installation des dépendances système ────────────────────────────────────
# tkinter nécessite python3-tk
# Les bibliothèques X11/display sont nécessaires pour afficher l'interface
# libglib2.0-0 et autres → dépendances de CustomTkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libx11-6 \
    libxft2 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# ── Dossier de travail dans le container ─────────────────────────────────────
WORKDIR /app

# ── Copie et installation des dépendances Python ────────────────────────────
# On copie requirements.txt EN PREMIER pour profiter du cache Docker
# Si requirements.txt ne change pas, cette étape n'est pas réexécutée
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copie du code source ─────────────────────────────────────────────────────
COPY . .

# ── Variable d'environnement pour l'affichage X11 ───────────────────────────
# DISPLAY=host.docker.internal:0 → redirige l'affichage vers XQuartz sur Mac
ENV DISPLAY=host.docker.internal:0

# ── Commande de démarrage ─────────────────────────────────────────────────────
CMD ["python", "main.py"]
