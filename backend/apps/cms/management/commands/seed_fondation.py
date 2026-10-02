"""Crée la page « Fondation PAD » (rubrique Engagements) et l'introduction de la rubrique.

Contenu repris de la page portdakar.sn/en/engagement/fondation. Idempotent ; --force réécrit.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.cms.home_blocks import library_image_id
from apps.cms.management.commands.seed_trafic_passagers import callout, h, image, p, ul
from apps.cms.models import StandardPage
from apps.core.blocks import ContentStreamBlock

NUMERO_VERT = "800 801 802"
SLUG = "fondation"
SOLIDARITY_TOUR_COUNT = 27


def _ol(items):
    return {
        "type": "paragraph",
        "value": "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>",
    }


def tournee_solidarite_gallery():
    images = []
    for n in range(1, SOLIDARITY_TOUR_COUNT + 1):
        num = f"{n:02d}"
        images.append(
            {
                "image": library_image_id(
                    f"fondation/tournee-solidarite/solidarite-{num}.jpg",
                    f"Tournée de solidarité {num}",
                ),
                "alt": f"Tournée de solidarité de la Fondation Port Autonome de Dakar, "
                f"photo {num}.",
                "caption": "",
            }
        )
    return {
        "type": "gallery",
        "value": {"title": "Tournée de solidarité", "images": images},
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
        image(
            "fondation/biennale-art-africain.png",
            "Biennale de l'art africain contemporain",
            "Stand de la Fondation Port Autonome de Dakar à la 14e Biennale de l'art africain "
            "contemporain.",
            "Participation à la 14e Biennale de l'art africain contemporain",
        ),
        image(
            "fondation/formation-femmes-touba.png",
            "Formation de femmes à Touba",
            "Une participante tient des légumes lors d'un atelier de transformation de fruits "
            "et légumes à Touba, organisé avec ONU Femmes.",
            "Formation de plus de 500 femmes de coopératives à Touba, avec ONU Femmes",
        ),
        image(
            "fondation/concours-general.png",
            "Concours général",
            "Remise de prix du concours général, en collaboration avec le ministère de "
            "l'Éducation nationale.",
            "Concours général, en collaboration avec le ministère de l'Éducation",
        ),
        image(
            "fondation/ecole-ngohe.png",
            "Bâtiment scolaire de Ngohé",
            "Bâtiment de six salles de classe entièrement équipées, offert par la Fondation.",
            "Don d'un bâtiment de six salles de classe au lycée de Ngohé",
        ),
        image(
            "fondation/journee-environnement.png",
            "Journée de l'environnement",
            "Équipe de volontaires de la Fondation lors d'une opération de nettoyage pour la "
            "Journée mondiale de l'environnement.",
            "Célébration de la Journée de l'environnement",
        ),
        image(
            "fondation/brigade-podor.png",
            "Brigade territoriale de Podor",
            "Bâtiment de la brigade territoriale construite et aménagée dans le département de "
            "Podor.",
            "Construction d'une brigade territoriale dans le département de Podor",
        ),
        image(
            "fondation/bouees-recyclees.png",
            "Jeux pour enfants fabriqués à partir de bouées recyclées",
            "Aire de jeux pour enfants fabriquée à partir de bouées de signalisation maritime "
            "hors d'usage, recyclées.",
            "Bouées recyclées transformées en équipements de jeux pour enfants",
        ),
        image(
            "fondation/campagne-medicale-salemata.png",
            "Campagne médicale à Salémata",
            "Rassemblement de la population lors d'une campagne médicale organisée par la "
            "Fondation à Salémata.",
            "Campagne médicale et réhabilitation de structures de santé à Salémata",
        ),
        image(
            "fondation/bloc-operatoire.png",
            "Bloc opératoire modernisé",
            "Salle du bloc opératoire modernisée grâce à l'appui de la Fondation.",
            "Modernisation d'un bloc opératoire",
        ),
        h("Tournée de solidarité"),
        p(
            "À l'occasion des grands événements religieux (Magal, Gamou), la Fondation mène une "
            "tournée de solidarité auprès des foyers religieux du pays, en signe de soutien et "
            "de partage."
        ),
        tournee_solidarite_gallery(),
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
            "La photo de l'administratrice, les chiffres à jour et les coordonnées propres à "
            "la Fondation sont à fournir par la Fondation.",
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
