"""Crée la page « Espace Pro » : passerelle vers le portail professionnel Atlantis.

Le Port Autonome de Dakar exploite déjà un portail professionnel externe (Atlantis) pour la
création de compte, la connexion et les déclarations de chiffre d'affaires des entreprises
agréées (transitaires, transporteurs, manutentionnaires, consignataires, shipchandlers) — voir
« Procédures et agréments ». Cette page présente l'offre et renvoie vers ce portail : elle
remplace un ancien formulaire de connexion local qui ne menait à aucun compte réel.
Idempotent ; --force réécrit le contenu.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Site

from apps.cms.management.commands.seed_trafic_passagers import callout, h, p, ul
from apps.cms.models import StandardPage
from apps.core.blocks import ContentStreamBlock

SLUG = "espace-pro"
PORTAL_URL = "https://atlantis.portdakar.sn"
SIGNUP_URL = "https://atlantis.portdakar.sn/creationcompte.padpublic?userParam=ADD"

PROFESSIONS = [
    "Transitaire",
    "Transporteur de conteneurs",
    "Manutentionnaire",
    "Consignataire",
    "Autorisation d'exercer à bord des navires",
    "Shipchandler",
]


def cta(label, url):
    return {"type": "cta", "value": {"label": label, "url": url}}


def espace_pro():
    return [
        p(
            "L'Espace Pro est le point d'accès des entreprises agréées du Port Autonome de "
            "Dakar au portail professionnel en ligne <strong>Atlantis</strong> : création de "
            "compte, connexion à vos démarches et déclaration de votre chiffre d'affaires."
        ),
        cta("Se connecter à Atlantis", PORTAL_URL),
        cta("Créer un compte professionnel", SIGNUP_URL),
        h("Qui peut y accéder ?"),
        p("L'Espace Pro s'adresse aux entreprises titulaires d'un agrément du port :"),
        ul(PROFESSIONS),
        h("Procédures et formulaires"),
        p(
            "Les pièces à fournir pour obtenir ou renouveler un agrément, et les formulaires "
            "de déclaration de chiffre d'affaires, sont réunis dans la rubrique "
            '<a href="/fr/opportunites-affaires/procedures-agrements/">Procédures et '
            "agréments</a>."
        ),
        callout(
            "À compléter",
            "Le détail des services disponibles dans le portail Atlantis (tableau de bord, "
            "historique des déclarations, assistance dédiée) est à préciser par le port.",
        ),
    ]


class Command(BaseCommand):
    help = "Crée la page Espace Pro (passerelle vers le portail Atlantis)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        root = Site.objects.get(is_default_site=True).root_page
        page = root.get_children().filter(slug=SLUG).first()
        if page is None:
            page = StandardPage(title="Espace Pro", slug=SLUG, show_in_menus=False)
            root.add_child(instance=page)
            created = True
        else:
            created = False
        page = page.specific
        if created or force or not len(page.body):
            page.body = ContentStreamBlock().to_python(espace_pro())
            page.save_revision().publish()
            self.stdout.write(f"Espace Pro : {'créée' if created else 'mise à jour'}.")
        else:
            self.stdout.write("Espace Pro : contenu déjà présent, ignoré (--force pour réécrire).")
