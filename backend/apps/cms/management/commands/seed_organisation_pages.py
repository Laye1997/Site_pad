"""Renseigne Statut et Mission, Administration et Assemblée Générale (contenu de l'ancien site).

Source : pages correspondantes de portdakar.sn (gouvernance de la SONAPAD). Par défaut, ne
modifie que les pages dont le contenu est vide ; --force réécrit le contenu.
"""

from django.core.management.base import BaseCommand

from apps.cms.models import StandardPage
from apps.core.blocks import ContentStreamBlock


def h(text, level="h2"):
    return {"type": "heading", "value": {"text": text, "level": level}}


def p(html):
    return {"type": "paragraph", "value": f"<p>{html}</p>"}


def ul(items):
    return {
        "type": "paragraph",
        "value": "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>",
    }


def statut_et_mission():
    return [
        p(
            "Depuis le 1er juillet 1987, le Port Autonome de Dakar est une société nationale au "
            "capital de 52 milliards de FCFA, en vertu de la loi n° 87-28 du 18 août 1987 "
            "modifiée."
        ),
        h("Missions"),
        ul(
            [
                "Exploitation et entretien du port maritime de Dakar et de ses dépendances, "
                "gestion de son domaine mobilier et immobilier",
                "Acquisition et exploitation d'établissements similaires",
                "Participation dans des sociétés commerciales",
                "Opérations commerciales, industrielles, mobilières, immobilières ou "
                "financières liées à son objet",
            ]
        ),
    ]


def administration():
    return [
        h("Conseil d'administration"),
        p(
            "La société est administrée par un conseil de 12 membres au plus (Présidence, "
            "Primature, ministères de tutelle et des finances, personnel, secteurs portuaires "
            "et commerciaux). Il délibère sur le plan stratégique, le budget, le patrimoine et "
            "les tarifs portuaires."
        ),
        h("Comité de direction"),
        p(
            "Il assure le contrôle permanent de la gestion entre les réunions du Conseil. "
            "Présidé par le président du Conseil ou un vice-président, il réunit des "
            "représentants des ministères de tutelle et trois membres élus par le Conseil."
        ),
        h("Directeur Général"),
        p(
            "Il assure la gestion générale de la société et veille à l'exécution des décisions "
            "des organes délibérants."
        ),
    ]


def assemblee_generale():
    return [
        h("Composition"),
        p(
            "17 membres votants (Présidence, Primature, ministères techniques et financiers, "
            "personnel, chambres de commerce, entreprises portuaires, représentants maliens, "
            "autorités militaires et judiciaires) et six membres à voix consultative, dont le "
            "Contrôleur financier et le Directeur Général."
        ),
        h("Assemblée générale ordinaire"),
        ul(
            [
                "Examine les rapports de gestion et approuve les comptes",
                "Nomme les commissaires aux comptes",
                "Approuve les conventions réglementées",
            ]
        ),
        h("Assemblée générale extraordinaire"),
        p(
            "Elle délibère sur toute modification du capital ou des statuts, sous la "
            "présidence du Président du Conseil d'administration."
        ),
    ]


PAGES = {
    "statut-et-mission": statut_et_mission,
    "administration": administration,
    "assemblee-generale": assemblee_generale,
}


class Command(BaseCommand):
    help = "Renseigne Statut et Mission, Administration et Assemblée Générale."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        for slug, builder in PAGES.items():
            page = StandardPage.objects.filter(slug=slug).first()
            if page is None:
                self.stdout.write(f"{slug} : page introuvable (lancez seed_site_structure).")
                continue
            if len(page.body) and not force:
                self.stdout.write(f"{page.title} : contenu déjà présent, ignoré.")
                continue
            raw = builder()
            page.body = ContentStreamBlock().to_python(raw)
            page.save_revision().publish()
            self.stdout.write(f"{page.title} : contenu enregistré ({len(raw)} blocs).")
