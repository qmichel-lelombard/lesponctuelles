"""Configuration partagee : pages a creer, leurs images et leur contenu.

Modifiez cette liste (ou les fichiers dans content/) pour ajuster le texte,
les photos prevues ou l'ordre des sections, puis relancez create_pages.py.
"""
import os

BASE_DIR = os.path.dirname(__file__)

PAGES = [
    {
        "slug": "chauffage",
        "title": "Chauffage",
        "content_file": os.path.join(BASE_DIR, "content", "chauffage.html"),
        "excerpt": (
            "Installation, entretien et depannage de chaudieres, pompes a "
            "chaleur et chauffage central a Enghien et dans un rayon de 50 km."
        ),
        "images": [
            {"key": "hero-chauffage", "filename": "hero-chauffage.jpg",
             "alt": "Chauffagiste en intervention a Enghien", "color": (198, 93, 42)},
            {"key": "chaudiere-condensation", "filename": "chaudiere-condensation.jpg",
             "alt": "Installation d'une chaudiere a condensation", "color": (176, 76, 34)},
            {"key": "pompe-a-chaleur", "filename": "pompe-a-chaleur.jpg",
             "alt": "Installation d'une pompe a chaleur", "color": (156, 64, 32)},
            {"key": "entretien-chaudiere", "filename": "entretien-chaudiere.jpg",
             "alt": "Entretien annuel d'une chaudiere", "color": (214, 116, 58)},
            {"key": "radiateurs", "filename": "radiateurs.jpg",
             "alt": "Pose de radiateurs et chauffage central", "color": (188, 84, 38),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2026/09/IMG-20260808-WA0009.jpg"},
            {"key": "depannage-chauffage", "filename": "depannage-chauffage.jpg",
             "alt": "Depannage chauffage en urgence", "color": (140, 55, 28)},
        ],
    },
    {
        "slug": "sanitaire",
        "title": "Sanitaire",
        "content_file": os.path.join(BASE_DIR, "content", "sanitaire.html"),
        "excerpt": (
            "Installation, renovation et depannage sanitaire (salle de bain, "
            "chauffe-eau, robinetterie) a Enghien et dans un rayon de 50 km."
        ),
        "images": [
            {"key": "hero-sanitaire", "filename": "hero-sanitaire.jpg",
             "alt": "Travaux de plomberie sanitaire a Enghien", "color": (36, 92, 122)},
            {"key": "installation-sanitaire", "filename": "installation-sanitaire.jpg",
             "alt": "Installation sanitaire complete", "color": (30, 80, 110)},
            {"key": "renovation-sdb", "filename": "renovation-sdb.jpg",
             "alt": "Renovation de salle de bain", "color": (24, 68, 96)},
            {"key": "chauffe-eau", "filename": "chauffe-eau.jpg",
             "alt": "Installation d'un chauffe-eau", "color": (44, 104, 134),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2026/09/chaufferie.png"},
            {"key": "depannage-plomberie", "filename": "depannage-plomberie.jpg",
             "alt": "Depannage fuite et debouchage", "color": (20, 60, 88)},
            {"key": "robinetterie", "filename": "robinetterie.jpg",
             "alt": "Pose de robinetterie", "color": (52, 112, 140)},
        ],
    },
    {
        "slug": "contact",
        "title": "Contact",
        "content_file": os.path.join(BASE_DIR, "content", "contact.html"),
        "excerpt": (
            "Contactez Guillaume Tessaro, plombier-chauffagiste independant a "
            "Enghien : telephone, adresse, horaires et formulaire de contact."
        ),
        "images": [
            {"key": "hero-contact", "filename": "hero-contact.jpg",
             "alt": "Enghien, zone d'intervention de Guillaume Tessaro", "color": (60, 60, 60),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2026/08/enghien.jpg"},
        ],
    },
    {
        # Reproduction de la page d'accueil (actuellement en Elementor) en
        # HTML/CSS simple, dans le meme style que les 3 pages ci-dessus.
        # Creee sous un slug distinct pour relecture : ne remplace pas
        # automatiquement la page d'accueil actuelle. Reutilise les memes
        # photos hero que chauffage/sanitaire (meme cle -> pas de doublon
        # grace au cache de televersement dans create_pages.py).
        "slug": "nouvel-accueil",
        "title": "Accueil (nouvelle version)",
        "content_file": os.path.join(BASE_DIR, "content", "accueil.html"),
        "excerpt": (
            "Guillaume Tessaro, plombier-chauffagiste independant a Enghien : "
            "chauffage, sanitaire, devis gratuit."
        ),
        "images": [
            {"key": "hero-chauffage", "filename": "hero-chauffage.jpg",
             "alt": "Chauffagiste en intervention a Enghien", "color": (198, 93, 42)},
            {"key": "hero-sanitaire", "filename": "hero-sanitaire.jpg",
             "alt": "Travaux de plomberie sanitaire a Enghien", "color": (36, 92, 122)},
            {"key": "bio-chauffe-eau", "filename": "bio-chauffe-eau.jpg",
             "alt": "Installation d'un chauffe-eau", "color": (60, 90, 110),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2025/08/WhatsApp-Image-2025-08-21-a-12.29.32_da86a4c9.jpg"},
            {"key": "bio-wc", "filename": "bio-wc.jpg",
             "alt": "Installation sanitaire d'un WC", "color": (90, 70, 60),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2025/08/WhatsApp-Image-2025-08-21-a-12.28.31_f4abe4f1.jpg"},
            {"key": "bio-chantier", "filename": "bio-chantier.jpg",
             "alt": "Guillaume Tessaro sur un chantier", "color": (70, 70, 70),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2025/08/WhatsApp-Image-2025-08-25-a-19.59.54_c3b4a43a.jpg"},
            {"key": "bio-chauffe-eau-2", "filename": "bio-chauffe-eau-2.jpg",
             "alt": "Installation d'un second chauffe-eau", "color": (50, 80, 100),
             "external_url": "https://guillaumetessaro.be/wp-content/uploads/2025/08/WhatsApp-Image-2025-08-21-a-12.28.31_a4c3a1a2.jpg"},
        ],
    },
]

# Coordonnees affichees sur la page Contact et dans le pied de page commun
# -- ajustez si elles changent.
CONTACT_INFO = {
    "phone_display": "0475 30 84 49",
    "phone_tel": "+32475308449",
    "email": "tessaro.guillaume@hotmail.com",
    "address": "7850 Enghien, Belgique",
    "hours": "Lundi - Samedi : 8h00 - 17h00",
    # Versions courtes utilisees dans le pied de page (comme sur la page d'accueil)
    "address_short": "7850 Enghien",
    "hours_short": "Lu-Sa 8:00 - 17:00",
    "facebook_url": "https://www.facebook.com/tessaro.guillaume/",
}

# Adresse utilisee pour centrer la carte du pied de page (repere approximatif,
# sans numero de rue -- coherent avec la carte de la page d'accueil).
FOOTER_MAP_QUERY = "Chaussée d'Ath, 7850 Enghien"

FOOTER_PARTIAL = os.path.join(BASE_DIR, "content", "_footer.html")

# URL du fichier logo (une fois televerse dans wp-admin > Medias) a utiliser
# dans le pied de page. Laissez vide pour afficher "Guillaume Tessaro" en
# texte a la place (pas de pictogramme). Peut aussi etre fourni via
# --logo-url.
FOOTER_LOGO_URL = "https://guillaumetessaro.be/wp-content/uploads/2025/08/logo-guillaume.png"

# Shortcode du formulaire de contact (ex: Contact Form 7) a inserer sur la
# page Contact, une fois le plugin installe et le formulaire cree dans
# wp-admin. Laissez vide pour afficher un message d'attente a la place.
# Peut aussi etre fourni via l'option --form-shortcode de create_pages.py.
CONTACT_FORM_SHORTCODE = ""
