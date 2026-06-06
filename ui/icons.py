"""
ui/icons.py — Icônes "au trait" minimalistes (style Lucide)
------------------------------------------------------------
Dessine des icônes monochromes au trait avec PIL et les retourne
sous forme de CTkImage. Évite les emojis colorés pour un rendu
minimaliste fidèle à l'app Next.js.

Usage:
    from ui.icons import get_icon
    img = get_icon("dashboard", "#2563EB", size=20)
    ctk.CTkButton(parent, image=img, text="Dashboard")
"""

from PIL import Image, ImageDraw, ImageFilter
import customtkinter as ctk

# Cache : (name, color, size) -> CTkImage
_CACHE: dict = {}

_SS = 4          # super-sampling (dessine en grand puis réduit = bords lisses)
_BASE = 24       # taille logique de la grille de dessin


def _rgba(hex_color: str):
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def _new(color):
    """Crée un canvas transparent + un drawer, à haute résolution."""
    s = _BASE * _SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    return img, d, _rgba(color), _SS


# ── Dessins individuels (coordonnées sur une grille 24x24, *_SS) ───────────────

def _draw_dashboard(d, c, k):
    """Grille 2x2 (LayoutDashboard)."""
    w = 2 * k
    r = 2 * k
    quads = [(3, 3, 10, 10), (13, 3, 21, 10), (3, 13, 10, 21), (13, 13, 21, 21)]
    for x0, y0, x1, y1 in quads:
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r,
                            outline=c, width=w)


def _draw_catalogue(d, c, k):
    """Livres alignés (Library) : 3 dos verticaux + 1 incliné."""
    w = 2 * k
    r = 1 * k
    spines = [(4, 5, 7, 20), (8, 4, 11, 20), (12, 6, 15, 20)]
    for x0, y0, x1, y1 in spines:
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r,
                            outline=c, width=w)
    # Livre incliné à droite
    d.line([(16 * k, 9 * k), (20 * k, 8 * k)], fill=c, width=w)
    d.line([(17 * k, 20 * k), (21 * k, 19 * k)], fill=c, width=w)
    d.line([(16 * k, 9 * k), (17 * k, 20 * k)], fill=c, width=w)
    d.line([(20 * k, 8 * k), (21 * k, 19 * k)], fill=c, width=w)


def _draw_gestion(d, c, k):
    """Base de données (cylindre)."""
    w = 2 * k
    # Ellipse du haut
    d.ellipse([5 * k, 3 * k, 19 * k, 8 * k], outline=c, width=w)
    # Côtés
    d.line([(5 * k, 5.5 * k), (5 * k, 18 * k)], fill=c, width=w)
    d.line([(19 * k, 5.5 * k), (19 * k, 18 * k)], fill=c, width=w)
    # Arc du bas
    d.arc([5 * k, 15 * k, 19 * k, 20 * k], start=0, end=180, fill=c, width=w)
    # Arc du milieu
    d.arc([5 * k, 9 * k, 19 * k, 14 * k], start=0, end=180, fill=c, width=w)


def _draw_logout(d, c, k):
    """Déconnexion (LogOut) : cadre + flèche sortante."""
    w = 2 * k
    # Cadre de gauche (ouvert à droite)
    d.line([(10 * k, 4 * k), (5 * k, 4 * k)], fill=c, width=w)
    d.line([(5 * k, 4 * k), (5 * k, 20 * k)], fill=c, width=w)
    d.line([(5 * k, 20 * k), (10 * k, 20 * k)], fill=c, width=w)
    # Flèche vers la droite
    d.line([(10 * k, 12 * k), (21 * k, 12 * k)], fill=c, width=w)
    d.line([(17 * k, 8 * k), (21 * k, 12 * k)], fill=c, width=w)
    d.line([(17 * k, 16 * k), (21 * k, 12 * k)], fill=c, width=w)


def _draw_book_open(d, c, k):
    """Livre ouvert (BookOpen) — utilisé pour le logo."""
    w = 2 * k
    # Reliure centrale
    d.line([(12 * k, 6 * k), (12 * k, 20 * k)], fill=c, width=w)
    # Page gauche
    d.line([(12 * k, 6 * k), (4 * k, 7.5 * k)], fill=c, width=w)
    d.line([(4 * k, 7.5 * k), (4 * k, 18 * k)], fill=c, width=w)
    d.line([(4 * k, 18 * k), (12 * k, 20 * k)], fill=c, width=w)
    # Page droite
    d.line([(12 * k, 6 * k), (20 * k, 7.5 * k)], fill=c, width=w)
    d.line([(20 * k, 7.5 * k), (20 * k, 18 * k)], fill=c, width=w)
    d.line([(20 * k, 18 * k), (12 * k, 20 * k)], fill=c, width=w)


def _draw_user(d, c, k):
    """Profil (User) : tête + épaules."""
    w = 2 * k
    d.ellipse([8 * k, 4 * k, 16 * k, 12 * k], outline=c, width=w)
    d.arc([4 * k, 14 * k, 20 * k, 28 * k], start=180, end=360, fill=c, width=w)


def _draw_shield(d, c, k):
    """Bouclier (Admin)."""
    w = 2 * k
    d.line([(12 * k, 3 * k), (5 * k, 6 * k)], fill=c, width=w)
    d.line([(12 * k, 3 * k), (19 * k, 6 * k)], fill=c, width=w)
    d.line([(5 * k, 6 * k), (5 * k, 12 * k)], fill=c, width=w)
    d.line([(19 * k, 6 * k), (19 * k, 12 * k)], fill=c, width=w)
    d.line([(5 * k, 12 * k), (12 * k, 21 * k)], fill=c, width=w)
    d.line([(19 * k, 12 * k), (12 * k, 21 * k)], fill=c, width=w)


def _draw_hash(d, c, k):
    """Dièse (#) — pour l'ID."""
    w = 2 * k
    d.line([(9 * k, 4 * k), (7 * k, 20 * k)], fill=c, width=w)
    d.line([(16 * k, 4 * k), (14 * k, 20 * k)], fill=c, width=w)
    d.line([(4 * k, 9 * k), (20 * k, 9 * k)], fill=c, width=w)
    d.line([(4 * k, 15 * k), (20 * k, 15 * k)], fill=c, width=w)


def _draw_bookmark(d, c, k):
    """Marque-page (Bookmark) — pour la catégorie."""
    w = 2 * k
    d.line([(6 * k, 4 * k), (18 * k, 4 * k)], fill=c, width=w)
    d.line([(6 * k, 4 * k), (6 * k, 21 * k)], fill=c, width=w)
    d.line([(18 * k, 4 * k), (18 * k, 21 * k)], fill=c, width=w)
    d.line([(6 * k, 21 * k), (12 * k, 16 * k)], fill=c, width=w)
    d.line([(18 * k, 21 * k), (12 * k, 16 * k)], fill=c, width=w)


def _draw_mappin(d, c, k):
    """Épingle (MapPin) — pour les exemplaires."""
    w = 2 * k
    d.ellipse([6 * k, 3 * k, 18 * k, 15 * k], outline=c, width=w)
    d.line([(7.5 * k, 12 * k), (12 * k, 21 * k)], fill=c, width=w)
    d.line([(16.5 * k, 12 * k), (12 * k, 21 * k)], fill=c, width=w)
    d.ellipse([10 * k, 7 * k, 14 * k, 11 * k], outline=c, width=w)


def _draw_plus(d, c, k):
    """Plus (+) — bouton Ajouter."""
    w = 2 * k
    d.line([(12 * k, 5 * k), (12 * k, 19 * k)], fill=c, width=w)
    d.line([(5 * k, 12 * k), (19 * k, 12 * k)], fill=c, width=w)


def _draw_pencil(d, c, k):
    """Crayon (Edit) — bouton Modifier."""
    w = 2 * k
    d.line([(5 * k, 19 * k), (16 * k, 8 * k)], fill=c, width=w)
    d.line([(16 * k, 8 * k), (19 * k, 11 * k)], fill=c, width=w)
    d.line([(19 * k, 11 * k), (8 * k, 22 * k)], fill=c, width=w)
    d.line([(5 * k, 19 * k), (8 * k, 22 * k)], fill=c, width=w)


def _draw_trash(d, c, k):
    """Poubelle (Trash) — bouton Supprimer."""
    w = 2 * k
    d.line([(5 * k, 7 * k), (19 * k, 7 * k)], fill=c, width=w)
    d.line([(9 * k, 7 * k), (10 * k, 4 * k)], fill=c, width=w)
    d.line([(10 * k, 4 * k), (14 * k, 4 * k)], fill=c, width=w)
    d.line([(14 * k, 4 * k), (15 * k, 7 * k)], fill=c, width=w)
    d.line([(6.5 * k, 7 * k), (7.5 * k, 20 * k)], fill=c, width=w)
    d.line([(7.5 * k, 20 * k), (16.5 * k, 20 * k)], fill=c, width=w)
    d.line([(16.5 * k, 20 * k), (17.5 * k, 7 * k)], fill=c, width=w)


def _draw_key(d, c, k):
    """Clé (Key) — configuration de la clé API."""
    w = 2 * k
    d.ellipse([4 * k, 4 * k, 11 * k, 11 * k], outline=c, width=w)
    d.line([(9.5 * k, 9.5 * k), (19 * k, 19 * k)], fill=c, width=w)
    d.line([(16 * k, 16 * k), (19 * k, 13 * k)], fill=c, width=w)
    d.line([(19 * k, 19 * k), (21 * k, 17 * k)], fill=c, width=w)


def _draw_sparkles(d, c, k):
    """Étincelles (Sparkles) — avatar de l'assistant IA."""
    big = [(12, 3), (14, 10), (21, 12), (14, 14), (12, 21),
           (10, 14), (3, 12), (10, 10)]
    d.polygon([(x * k, y * k) for x, y in big], fill=c)
    small = [(19, 3), (19.8, 5.2), (22, 6), (19.8, 6.8),
             (19, 9), (18.2, 6.8), (16, 6), (18.2, 5.2)]
    d.polygon([(x * k, y * k) for x, y in small], fill=c)


def _draw_chat(d, c, k):
    """Bulle de discussion (MessageCircle)."""
    w = 2 * k
    d.rounded_rectangle([4 * k, 4 * k, 20 * k, 16 * k], radius=4 * k,
                        outline=c, width=w)
    # Petite queue en bas à gauche
    d.line([(8 * k, 16 * k), (6 * k, 21 * k)], fill=c, width=w)
    d.line([(6 * k, 21 * k), (12 * k, 16 * k)], fill=c, width=w)
    # Trois points
    for cx in (9, 12, 15):
        d.ellipse([(cx - 0.6) * k, 9.4 * k, (cx + 0.6) * k, 10.6 * k], fill=c)


def _draw_send(d, c, k):
    """Avion en papier (Send)."""
    w = 2 * k
    d.line([(21 * k, 3 * k), (3 * k, 11 * k)], fill=c, width=w)
    d.line([(21 * k, 3 * k), (13 * k, 21 * k)], fill=c, width=w)
    d.line([(3 * k, 11 * k), (13 * k, 21 * k)], fill=c, width=w)
    d.line([(3 * k, 11 * k), (13 * k, 13 * k)], fill=c, width=w)
    d.line([(13 * k, 13 * k), (13 * k, 21 * k)], fill=c, width=w)


def _draw_close(d, c, k):
    """Croix (X)."""
    w = 2 * k
    d.line([(6 * k, 6 * k), (18 * k, 18 * k)], fill=c, width=w)
    d.line([(18 * k, 6 * k), (6 * k, 18 * k)], fill=c, width=w)


def _draw_search(d, c, k):
    """Loupe (Search)."""
    w = 2 * k
    d.ellipse([5 * k, 5 * k, 15 * k, 15 * k], outline=c, width=w)
    d.line([(14 * k, 14 * k), (20 * k, 20 * k)], fill=c, width=w)


def _draw_check(d, c, k):
    """Coche (Check) — pour Disponibles."""
    w = 2 * k
    d.line([(5 * k, 12 * k), (10 * k, 17 * k)], fill=c, width=w)
    d.line([(10 * k, 17 * k), (19 * k, 7 * k)], fill=c, width=w)


def _draw_arrowout(d, c, k):
    """Flèche sortante (haut-droite) — pour Empruntés."""
    w = 2 * k
    d.line([(6 * k, 18 * k), (18 * k, 6 * k)], fill=c, width=w)
    d.line([(9 * k, 6 * k), (18 * k, 6 * k)], fill=c, width=w)
    d.line([(18 * k, 6 * k), (18 * k, 15 * k)], fill=c, width=w)


def _draw_layers(d, c, k):
    """Pile / couches (Layers) — pour le Total des livres."""
    w = 2 * k
    d.polygon([(12 * k, 4 * k), (20 * k, 8 * k), (12 * k, 12 * k), (4 * k, 8 * k)],
              outline=c, width=w)
    d.line([(4 * k, 12 * k), (12 * k, 16 * k)], fill=c, width=w)
    d.line([(20 * k, 12 * k), (12 * k, 16 * k)], fill=c, width=w)
    d.line([(4 * k, 16 * k), (12 * k, 20 * k)], fill=c, width=w)
    d.line([(20 * k, 16 * k), (12 * k, 20 * k)], fill=c, width=w)


_DRAWERS = {
    "check": _draw_check,
    "arrowout": _draw_arrowout,
    "layers": _draw_layers,
    "sparkles": _draw_sparkles,
    "key": _draw_key,
    "chat": _draw_chat,
    "send": _draw_send,
    "close": _draw_close,
    "search": _draw_search,
    "plus": _draw_plus,
    "pencil": _draw_pencil,
    "trash": _draw_trash,
    "dashboard": _draw_dashboard,
    "catalogue": _draw_catalogue,
    "gestion": _draw_gestion,
    "logout": _draw_logout,
    "book": _draw_book_open,
    "user": _draw_user,
    "shield": _draw_shield,
    "hash": _draw_hash,
    "bookmark": _draw_bookmark,
    "mappin": _draw_mappin,
}


def _icon_image(name: str, color: str, size: int) -> Image.Image:
    """Dessine l'icône et retourne une image PIL RGBA (anti-aliasée)."""
    img, d, c, k = _new(color)
    drawer = _DRAWERS.get(name)
    if drawer:
        drawer(d, c, k)
    return img.resize((size, size), Image.LANCZOS)


def get_icon(name: str, color: str, size: int = 20) -> ctk.CTkImage:
    """Retourne une CTkImage de l'icône au trait demandée (avec cache)."""
    key = (name, color, size)
    if key in _CACHE:
        return _CACHE[key]

    img = _icon_image(name, color, size)
    ck = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    _CACHE[key] = ck
    return ck


def get_fab(icon: str = "chat", circle: str = "#2563EB", glow: str = "#3B82F6",
            display: int = 100) -> ctk.CTkImage:
    """
    Bouton flottant (FAB) façon "bulle de chat" avec halo lumineux flou,
    exactement comme la photo : cercle bleu + glow + icône blanche centrée.
    """
    key = ("fab", icon, circle, glow, display)
    if key in _CACHE:
        return _CACHE[key]

    ss = 4
    S = display * ss
    cx = cy = S // 2

    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # 1) Halo : disque coloré flouté qui s'estompe vers les bords
    glow_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gr = int(S * 0.36)
    gr_col = _rgba(glow)[:3] + (200,)
    gd.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=gr_col)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(S * 0.07))
    base = Image.alpha_composite(base, glow_layer)

    # 2) Cercle plein (le bouton)
    d = ImageDraw.Draw(base)
    cr = int(S * 0.30)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=_rgba(circle))

    # 3) Icône blanche centrée
    isz = int(S * 0.26)
    icon_img = _icon_image(icon, "#FFFFFF", isz)
    base.alpha_composite(icon_img, (cx - isz // 2, cy - isz // 2))

    out = base.resize((display, display), Image.LANCZOS)
    ck = ctk.CTkImage(light_image=out, dark_image=out, size=(display, display))
    _CACHE[key] = ck
    return ck
