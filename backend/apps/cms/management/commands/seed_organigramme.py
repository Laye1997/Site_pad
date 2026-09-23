"""Remplit la page « Organigramme » (Nous découvrir > Présentation > Organisation).

Deux sections : la structure hiérarchique complète (gouvernance, Directeur Général, Secrétariat
Général, 8 directions et leurs départements — reprise de l'organigramme fonctionnel officiel du
port), puis un trombinoscope avec les responsables identifiés et leur photo, repris de
portdakar.sn (Nous découvrir > Organigramme). Les photos sont importées dans la médiathèque
Wagtail. Tout est modifiable depuis l'admin (textes, unités, photos). Idempotent ; --force réécrit.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.cms.home_blocks import library_image_id
from apps.core.blocks import ContentStreamBlock

SLUG = "organigramme"

# Structure hiérarchique complète (organigramme fonctionnel officiel).
STRUCTURE = {
    "governance_title": "Conseil d'Administration",
    "governance_branches": ["Comités spécialisés", "Comité de direction"],
    "dg_title": "Directeur Général",
    "dg_attached": ["Cabinet du DG", "Conseillers techniques"],
    "dg_cells": [
        "Cellule Contrôle de Gestion et Pilotage de la Performance",
        "Cellule Audit et Contrôle Interne",
        "Cellule Communication",
        "Cellule Qualité, Sécurité, Sûreté, Environnement (QSSE)",
    ],
    "secretariat_title": "Secrétariat Général",
    "secretariat_cells": [
        "Cellule de Passation des Marchés",
        "Cellule des Moyens Généraux et Archives",
        "Cellule Project Management Office (PMO)",
    ],
    "directions": [
        {
            "title": "Direction de la Stratégie et des Partenariats",
            "departments": [
                "Département Stratégie et Développement",
                "Département Partenariats et Coopération",
            ],
        },
        {
            "title": "Direction Technique",
            "departments": [
                "Département Études, Ouvrages et Maintenance",
                "Département Phares et Balises",
            ],
        },
        {
            "title": "Direction de l'Exploitation / Haut Commandement",
            "departments": [
                "Département Capitainerie",
                "Département Opérations",
                "Département Gestion du Trafic Passagers",
                "Département Sécurité et Sûreté",
            ],
        },
        {
            "title": "Direction Juridique",
            "departments": [
                "Département Juridique",
                "Département Affaires Domaniales",
                "Département Valorisation du Patrimoine",
            ],
        },
        {
            "title": "Direction Commerciale",
            "departments": [
                "Département Gestion de la Clientèle",
                "Département Facturation",
            ],
        },
        {
            "title": "Direction Financière et Comptable",
            "departments": [
                "Département Gestion Comptable et Financière",
                "Département Contrôle Financier et Recouvrement",
            ],
        },
        {
            "title": "Direction du Capital Humain et de l'Organisation",
            "departments": [
                "Département Administration du Capital Humain",
                "Département Organisation et Développement du Capital Humain",
            ],
        },
        {
            "title": "Direction du Digital",
            "departments": [
                "Département Système d'Information, Exploitation et Sécurité",
                "Département Infrastructures et Transformation",
            ],
        },
    ],
    "regional_title": "Ports régionaux (04)",
}

# Trombinoscope : (fichier dans static/img/organigramme ou None, nom, fonction)
GROUPS = [
    (
        "Direction générale",
        True,
        [("doune-pathe-mbengue", "Doune Pathé MBENGUE", "Directeur Général")],
    ),
    (
        "Cellules rattachées à la Direction générale",
        False,
        [
            (
                "khady-diop",
                "Khady DIOP",
                "Cellule Contrôle de Gestion et Pilotage de la Performance",
            ),
            ("alioune-fall", "Alioune FALL", "Cellule Audit et Contrôle Interne"),
            ("bineta-diop", "Bineta DIOP", "Cellule Communication"),
            (
                "rokhaya-ly",
                "Rokhaya LY",
                "Cellule Qualité, Sécurité, Sûreté, Environnement (QSSE)",
            ),
        ],
    ),
    (
        "Secrétariat général",
        False,
        [
            ("mactar-diallo", "Mactar DIALLO", "Secrétaire Général"),
            ("baila-dia", "Baila DIA", "Cellule de Passation des Marchés"),
            ("assane-sarr", "Assane SARR", "Cellule des Moyens Généraux et Archives"),
            ("mohamed-dia", "Mohamed DIA", "Cellule Project Management Office (PMO)"),
        ],
    ),
    (
        "Directions",
        False,
        [
            (
                "momar-ngary-ba",
                "Momar Ngary BA",
                "Direction de la Stratégie et des Partenariats",
            ),
            ("ousseynou-ndiaye", "Ousseynou NDIAYE", "Direction Technique"),
            (
                "ibrahima-diaw",
                "Ibrahima DIAW",
                "Direction de l'Exploitation / Haut Commandement",
            ),
            (None, "À compléter", "Direction Juridique"),
            ("pape-ibrahima-sow", "Pape Ibrahima SOW", "Direction Commerciale"),
            ("babacar-niang", "Babacar NIANG", "Direction Financière et Comptable"),
            (
                "mandoye-ndoye",
                "Mandoye NDOYE",
                "Direction du Capital Humain et de l'Organisation",
            ),
            ("pape-mass-diallo", "Pape Mass DIALLO", "Direction du Digital"),
        ],
    ),
    (
        "Ports régionaux",
        False,
        [
            ("coumba-diouf-niang", "Coumba Diouf NIANG", "Port de Ziguinchor"),
            ("abdoulaye-sogue", "Abdoulaye SOGUE", "Port de Kaolack"),
            ("ngor-dione", "Ngor DIONE", "Port de Ndakhonga – Foundiougne"),
            ("el-hadji-ndiogou-sy", "El Hadji Ndiogou SY", "Port de Saint-Louis"),
        ],
    ),
]


def organigramme():
    groups = []
    for title, featured, members in GROUPS:
        groups.append(
            {
                "title": title,
                "featured": featured,
                "members": [
                    {
                        "image": (
                            library_image_id(f"organigramme/{slug}.jpg", f"Organigramme — {name}")
                            if slug
                            else None
                        ),
                        "name": name,
                        "role": role,
                    }
                    for slug, name, role in members
                ],
            }
        )
    return [
        {"type": "heading", "value": {"text": "Structure de l'organigramme", "level": "h2"}},
        {"type": "org_structure", "value": STRUCTURE},
        {"type": "heading", "value": {"text": "Responsables par direction", "level": "h2"}},
        {"type": "org_chart", "value": {"groups": groups}},
        {
            "type": "callout",
            "value": {
                "title": "À compléter",
                "body": (
                    "Le nom du responsable de la Direction Juridique n'est pas encore publié "
                    "par le port ; à mettre à jour dès qu'il sera communiqué."
                ),
            },
        },
    ]


class Command(BaseCommand):
    help = "Remplit la page Organigramme (structure hiérarchique, noms, fonctions, photos)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        root = Site.objects.get(is_default_site=True).root_page
        page = Page.objects.descendant_of(root).filter(slug=SLUG).first()
        if page is None:
            self.stdout.write("Page « Organigramme » introuvable : lancez seed_site_structure.")
            return
        page = page.specific
        if not force and any(block.block_type == "org_structure" for block in page.body):
            self.stdout.write(
                "Organigramme : contenu déjà présent, ignoré (--force pour réécrire)."
            )
            return
        page.body = ContentStreamBlock().to_python(organigramme())
        page.save_revision().publish()
        self.stdout.write("Organigramme : page remplie.")
