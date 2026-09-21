"""Renseigne la rubrique « Marchandises » et ses 3 sous-pages.

Sources : pages portdakar.sn « Manutention » et « Stockage/Entreposage ». La page « Enlèvement de
marchandises » n'existe plus sur l'ancien site : elle ne reprend que des informations déjà publiées
par le PAD (durées de stockage gratuit, échange électronique des BAD, numéro vert) et doit être
complétée par la direction commerciale. Ne modifie que les pages vides ; --force réécrit.
"""

from django.core.management.base import BaseCommand

from apps.cms.management.commands.seed_trafic_passagers import (
    callout,
    contact,
    h,
    image,
    p,
    table,
    ul,
)
from apps.core.blocks import ContentStreamBlock
from apps.services.models import ServicePage

SECTION_SLUG = "marchandises"


def marchandises():
    return (
        "Manutention, stockage et enlèvement des marchandises au port.",
        [
            image(
                "marchandises-chargement.jpg",
                "Chargement de marchandises au port",
                "Un chariot élévateur charge des sacs de marchandises sur le terre-plein du port.",
            ),
            p(
                "Le Port Autonome de Dakar accueille les marchandises depuis leur arrivée à quai "
                "jusqu'à leur enlèvement : chargement et déchargement, stockage sur les "
                "terre-pleins et dans les hangars, puis sortie du port."
            ),
            h("Nos services"),
            ul(
                [
                    "<b>Manutention</b> : opérations de chargement et de déchargement, confiées "
                    "à des opérateurs privés ;",
                    "<b>Stockage et entreposage</b> : terre-pleins banalisés ou amodiés, hangars "
                    "et aires de dépôt ;",
                    "<b>Enlèvement de marchandises</b> : sortie des marchandises du port.",
                ]
            ),
            contact(),
        ],
    )


def manutention():
    return (
        "Le chargement et le déchargement des marchandises, confiés à des opérateurs privés.",
        [
            image(
                "origine/terminal_a_conteneur2.jpg",
                "Terminal à conteneurs du port",
                "Terminal à conteneurs du Port Autonome de Dakar : piles de conteneurs et "
                "tracteur avec remorque.",
            ),
            p(
                "La manutention est l'ensemble des opérations de chargement et de déchargement "
                "depuis l'arrivée de la marchandise jusqu'à son arrimage à bord du navire ou son "
                "entreposage sur les terre-pleins."
            ),
            p(
                "En vue d'optimiser les conditions d'escale, l'activité de manutention est "
                "confiée à des opérateurs privés."
            ),
            h("Les opérateurs"),
            ul(["DP World", "Bolloré Transport &amp; Logistics", "Necotrans", "Sea Invest"]),
            p(
                "Leur arrivée a permis de relever considérablement le niveau d'équipement du port, "
                "d'augmenter la capacité de manutention et de réduire le temps d'immobilisation "
                "des navires."
            ),
            h("Équipements"),
            ul(
                [
                    "Une grue Manitowoc Grove GMK 5200",
                    "Une grue Pinguely TT 286 X",
                    "Un camion plateforme élévatrice à nacelle Time VT 48 NE",
                ]
            ),
            image(
                "origine/banniere-grue.jpg",
                "Grues du port",
                "Quatre vues des grues mobiles jaunes utilisées pour la manutention au port.",
            ),
            contact(),
        ],
    )


def stockage():
    return (
        "Les terre-pleins, hangars et aires de stockage du port, et les durées de stockage "
        "gratuit.",
        [
            image(
                "origine/platefprme.jpg",
                "Plateforme logistique du port",
                "Vue aérienne d'une plateforme logistique du port, avec ses hangars et ses aires "
                "de stationnement.",
            ),
            p("Le port attribue ses terre-pleins selon deux régimes :"),
            ul(
                [
                    "<b>les terre-pleins banalisés</b> : attribués selon les disponibilités ;",
                    "<b>les terre-pleins amodiés</b> : loués pour une longue durée, "
                    "généralement de 9 à 25 ans.",
                ]
            ),
            h("Durées de stockage gratuit sur les terre-pleins banalisés"),
            table(
                ["Type de marchandise", "Durée gratuite"],
                [
                    [
                        "Marchandises conventionnelles et véhicules à destination du Sénégal",
                        "7 jours",
                    ],
                    ["Marchandises conventionnelles en transit", "20 jours"],
                    ["Véhicules en transit", "12 jours"],
                ],
            ),
            h("Capacités de stockage"),
            table(
                ["Type de stockage", "Capacité"],
                [
                    ["Stockage couvert (hangars)", "98 351 m²"],
                    ["Stockage à l'air libre", "216 309 m²"],
                    ["Aires de dépôt de conteneurs", "324 208 m²"],
                    ["Stockage frigorifique", "15 000 m²"],
                    ["Stockage d'hydrocarbures", "290 000 m³"],
                ],
            ),
            contact(),
        ],
    )


def enlevement():
    return (
        "La sortie des marchandises du port : durées de stockage gratuit et échange "
        "électronique des bons à délivrer.",
        [
            p(
                "L'enlèvement des marchandises intervient après leur déchargement et, le cas "
                "échéant, leur stockage sur les terre-pleins du port."
            ),
            h("Durées de stockage gratuit"),
            p(
                "Sur les terre-pleins banalisés, le stockage est gratuit pendant 7 jours pour les "
                "marchandises conventionnelles et les véhicules à destination du Sénégal, 20 jours "
                "pour les marchandises conventionnelles en transit et 12 jours pour les véhicules "
                "en transit. Le détail figure dans la page « Stockage / entreposage »."
            ),
            h("Bons à délivrer (BAD)"),
            p(
                "Le Port Autonome de Dakar et la Direction Générale des Douanes sénégalaises ont "
                "annoncé le lancement de l'échange électronique des Bons à Délivrer (BAD), avec "
                "une phase pilote à partir du 2 janvier 2026."
            ),
            callout(
                "Page à compléter",
                "La procédure détaillée d'enlèvement (pièces à fournir, guichets, horaires) est "
                "à renseigner par la direction concernée.",
            ),
            contact(),
        ],
    )


PAGES = {
    "marchandises": marchandises,
    "manutention": manutention,
    "stockage-entreposage": stockage,
    "enlevement-marchandises": enlevement,
}


class Command(BaseCommand):
    help = "Renseigne Marchandises et ses sous-pages."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        section = ServicePage.objects.filter(slug=SECTION_SLUG).first()
        if section is None:
            self.stdout.write("Rubrique introuvable : lancez seed_site_structure.")
            return
        for slug, builder in PAGES.items():
            page = section if slug == SECTION_SLUG else section.get_children().filter(slug=slug)
            page = page if slug == SECTION_SLUG else page.first()
            if page is None:
                self.stdout.write(f"{slug} : page introuvable.")
                continue
            page = page.specific
            if len(page.body) and not force:
                self.stdout.write(f"{page.title} : contenu déjà présent, ignoré.")
                continue
            summary, raw = builder()
            page.summary = summary
            page.body = ContentStreamBlock().to_python(raw)
            page.save_revision().publish()
            self.stdout.write(f"{page.title} : contenu enregistré ({len(raw)} blocs).")
