"""Importe le calendrier des croisières de l'ancien site et relie la page « Croisières ».

Idempotent : une escale déjà présente (même date et même navire) n'est pas dupliquée.
"""

import datetime as dt

from django.core.management.base import BaseCommand
from wagtail.models import Page
from wagtail.rich_text import RichText

from apps.navires.croisieres_data import CROISIERES
from apps.navires.models import Croisiere


class Command(BaseCommand):
    help = "Importe les escales de croisière et pointe la page Infos pratiques vers le calendrier."

    def handle(self, *args, **options):
        created = 0
        for day, month, year, navire, poste, consignataire in CROISIERES:
            _, was_created = Croisiere.objects.get_or_create(
                date=dt.date(year, month, day),
                navire=navire,
                defaults={"poste": poste, "consignataire": consignataire},
            )
            created += int(was_created)
        self.stdout.write(f"{created} escale(s) de croisière importée(s).")
        self._link_page()

    def _link_page(self):
        """La page éditoriale « Croisières » renvoie vers le calendrier dynamique."""
        page = Page.objects.filter(slug="croisieres").specific().first()
        if page is None or not hasattr(page, "body") or len(page.body):
            return
        page.body = [
            (
                "paragraph",
                RichText(
                    "<p>Le calendrier des escales de croisière est consultable ici : "
                    '<a href="/fr/navires/croisieres/">escales de croisière à venir et passées</a>.'
                    "</p>"
                ),
            )
        ]
        page.save_revision().publish()
        self.stdout.write("Page « Croisières » : lien vers le calendrier ajouté.")
