"""Crée la page « Fondation PAD » (rubrique Engagements) et l'introduction de la rubrique.

Contenu repris de la page portdakar.sn/en/engagement/fondation. Idempotent ; --force réécrit.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.cms.management.commands.seed_trafic_passagers import callout, h, p, ul
from apps.cms.models import StandardPage
from apps.core.blocks import ContentStreamBlock

NUMERO_VERT = "800 801 802"
SLUG = "fondation"


def _ol(items):
    return {
        "type": "paragraph",
        "value": "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>",
    }


def fondation():
    return [
        p(
            "La Fondation Port Autonome de Dakar est l'organe d'action sociale du port : elle "
            "conduit des actions en faveur des populations vulnérables du Sénégal."
        ),
        h("Historique de la Fondation"),
        p(
            "La Fondation a été créée en 2018 pour contribuer aux objectifs du Plan Sénégal "
            "Émergent, en particulier l'appui aux populations vulnérables. Elle répond aussi "
            "aux recommandations des auditeurs sur la rationalisation des subventions."
        ),
        h("Mission"),
        p(
            "La Fondation vise à améliorer les conditions de vie des populations vulnérables du "
            "Sénégal, dans les domaines suivants :"
        ),
        ul(
            [
                "<b>Santé</b> : assistance médicale, modernisation des infrastructures, "
                "renforcement des ressources sanitaires, soutien aux personnes âgées ;",
                "<b>Environnement</b> : préservation des écosystèmes, protection des océans et "
                "du littoral, promotion de la pêche artisanale ;",
                "<b>Éducation</b> : appui à la scolarisation, développement des infrastructures, "
                "promotion de l'excellence scientifique, bourses ;",
                "<b>Formation et insertion</b> : formation professionnelle des jeunes, "
                "développement des compétences pour les métiers portuaires, emploi des "
                "personnes en situation de handicap ;",
                "<b>Culture et sport</b> : promotion de la culture sénégalaise, activités "
                "sportives, événements religieux.",
            ]
        ),
        h("Objectifs"),
        _ol(
            [
                "Atteindre 100 % de conformité aux exigences applicables ;",
                "Adopter à 80 % les principes de développement durable dans les initiatives "
                "sociales ;",
                "Sécuriser 50 % du financement des projets grâce à des partenariats avec des "
                "bailleurs.",
            ]
        ),
        h("Quelques réalisations"),
        ul(
            [
                "Participation à la 14e Biennale de l'art africain contemporain ;",
                "Formation de plus de 500 femmes de coopératives à Touba, avec ONU Femmes ;",
                "Concours général, en collaboration avec le ministère de l'Éducation ;",
                "Don d'un bâtiment de six salles de classe au lycée de Ngohé ;",
                "Célébration de la Journée de l'environnement ;",
                "Construction d'une brigade territoriale dans le département de Podor ;",
                "Bouées recyclées transformées en équipements de jeux pour enfants ;",
                "Campagnes médicales et réhabilitation de structures de santé à Salémata et "
                "Missirah Bakaouka ;",
                "Modernisation d'un bloc opératoire.",
            ]
        ),
        h("Le mot de l'administratrice"),
        p(
            "Madame Diouma TIRERA, administratrice de la Fondation, réaffirme l'engagement de la "
            "Fondation à réduire les inégalités sociales par des programmes fondés sur les "
            "valeurs « SUCCESS » : Social, Universalité, Créativité, Conformité, Excellence, "
            "Satisfaction."
        ),
        callout(
            "Contact",
            f"Numéro vert du Port Autonome de Dakar : {NUMERO_VERT}. Contacts complets : "
            "rubrique « Infos pratiques ».",
        ),
        callout(
            "À compléter",
            "Les photos, les chiffres à jour et les coordonnées propres à la Fondation sont à "
            "fournir par la Fondation.",
        ),
    ]


ENGAGEMENTS = [
    p(
        "Le Port Autonome de Dakar inscrit son activité dans une démarche responsable : "
        "qualité, sécurité, environnement et action sociale."
    ),
    ul(
        [
            '<a href="/fr/engagements/qsse-rse/">QSSE et RSE</a> : politique qualité, sécurité, '
            "sûreté et environnement, et certifications ISO ;",
            '<a href="/fr/engagements/fondation/">Fondation PAD</a> : actions en faveur des '
            "populations vulnérables.",
        ]
    ),
]


class Command(BaseCommand):
    help = "Crée la page Fondation PAD et l'introduction de la rubrique Engagements."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        root = Site.objects.get(is_default_site=True).root_page
        parent = Page.objects.descendant_of(root).filter(slug="engagements").first()
        if parent is None:
            self.stdout.write("Rubrique « Engagements » introuvable : lancez seed_site_structure.")
            return
        parent = parent.specific
        if force or not len(parent.body):
            parent.body = ContentStreamBlock().to_python(ENGAGEMENTS)
            parent.save_revision().publish()
            self.stdout.write("Engagements : introduction enregistrée.")
        page = parent.get_children().filter(slug=SLUG).first()
        if page is None:
            page = StandardPage(title="Fondation PAD", slug=SLUG, show_in_menus=True)
            parent.add_child(instance=page)
            created = True
        else:
            created = False
        page = page.specific
        if created or force or not len(page.body):
            page.body = ContentStreamBlock().to_python(fondation())
            page.save_revision().publish()
            self.stdout.write(f"Fondation PAD : {'créée' if created else 'mise à jour'}.")
        else:
            self.stdout.write("Fondation PAD : contenu déjà présent, ignoré.")
