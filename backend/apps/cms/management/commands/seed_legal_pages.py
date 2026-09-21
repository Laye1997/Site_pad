"""Crée les pages légales (brouillons) : mentions légales, confidentialité, accessibilité,
plan du site.

Les pages sont créées NON PUBLIÉES : les informations marquées « À compléter » doivent être
renseignées et validées par le PAD (service juridique / DPO) avant publication dans l'admin.
Une page publiée apparaît automatiquement dans le pied de page.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Site
from wagtail.rich_text import RichText

from apps.cms.models import StandardPage

TODO = "[À compléter par le PAD]"


def _h(text):
    return ("heading", {"text": text, "level": "h2"})


def _p(html):
    return ("paragraph", RichText(f"<p>{html}</p>"))


PAGES = [
    (
        "Mentions légales",
        "mentions-legales",
        [
            _h("Éditeur du site"),
            _p("Port Autonome de Dakar (PAD), établissement public. Numéro vert : 800 801 802."),
            _p(f"Adresse du siège : {TODO}"),
            _p(f"Directeur de la publication : {TODO}"),
            _h("Hébergement"),
            _p(f"Hébergeur et localisation des serveurs : {TODO}"),
            _h("Propriété intellectuelle"),
            _p(
                "Les contenus du site (textes, images, vidéos, logos) sont la propriété du "
                f"Port Autonome de Dakar ou de leurs auteurs. Conditions de réutilisation : {TODO}"
            ),
            _h("Contact"),
            _p("Pour toute question sur le site, utilisez la page Contacts."),
        ],
    ),
    (
        "Politique de confidentialité",
        "confidentialite",
        [
            _h("Responsable du traitement"),
            _p(f"Port Autonome de Dakar. Délégué à la protection des données : {TODO}"),
            _h("Données collectées et finalités"),
            _p(
                "Formulaires de candidature (recrutement) et espace professionnel : gestion des "
                f"candidatures et des accès. Base légale, durées de conservation : {TODO}"
            ),
            _h("Cookies et mesure d'audience"),
            _p(
                "Le site n'utilise que les cookies nécessaires à son fonctionnement. Aucun traceur "
                "de mesure d'audience n'est déposé sans votre accord ; vous pouvez modifier votre "
                "choix à tout moment via « Gérer mes cookies » en pied de page."
            ),
            _h("Vos droits"),
            _p(
                "Conformément à la loi sénégalaise n° 2008-12 sur la protection des données à "
                "caractère personnel et, le cas échéant, au RGPD, vous disposez d'un droit "
                f"d'accès, de rectification, d'opposition et de suppression. Contact : {TODO}"
            ),
        ],
    ),
    (
        "Déclaration d'accessibilité",
        "accessibilite",
        [
            _h("Engagement"),
            _p(
                "Le Port Autonome de Dakar s'engage à rendre son site accessible conformément au "
                "RGAA 4 (WCAG 2.1, niveau AA)."
            ),
            _h("État de conformité"),
            _p(
                "L'audit de conformité RGAA n'a pas encore été réalisé : le site est en cours de "
                f"refonte. Résultat de l'audit et taux de conformité : {TODO}"
            ),
            _h("Signaler un problème"),
            _p(f"Si vous ne parvenez pas à accéder à un contenu, contactez-nous : {TODO}"),
        ],
    ),
    (
        "Plan du site",
        "plan-du-site",
        [
            _h("Rubriques"),
            _p(
                "Nous découvrir, Nos services, Opportunités d'affaires, Espace média, "
                "Infos pratiques, Engagements, Espace Pro et recrutement."
            ),
        ],
    ),
]


class Command(BaseCommand):
    help = "Crée les pages légales en brouillon (non publiées) sans écraser l'existant."

    def handle(self, *args, **options):
        root = Site.objects.get(is_default_site=True).root_page.specific
        for title, slug, body in PAGES:
            if root.get_children().filter(slug=slug).exists():
                self.stdout.write(f"Existe déjà : {slug}")
                continue
            page = StandardPage(title=title, slug=slug, body=body, live=False)
            root.add_child(instance=page)
            self.stdout.write(f"Brouillon créé : {slug}")
