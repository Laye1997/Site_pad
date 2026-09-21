"""Remplit la base avec des escales d'exemple."""

import datetime as dt

from django.core.management.base import BaseCommand

from apps.navires.models import Escale


class Command(BaseCommand):
    help = "Crée des escales d'exemple pour le mouvement des navires."

    def handle(self, *args, **options):
        fixtures = [
            {
                "navire": "MV Aster",
                "type_navire": "conteneur",
                "pavillon": "France",
                "provenance": "Le Havre",
                "destination": "Dakar",
                "quai": "Quai 2",
                "date_arrivee": dt.date(2026, 9, 18),
                "date_depart": None,
                "statut": "attendu",
                "consignataire": "Dakar Port Services",
            },
            {
                "navire": "MV Borneo",
                "type_navire": "cargo",
                "pavillon": "Panama",
                "provenance": "Abidjan",
                "destination": "Nouadhibou",
                "quai": "Quai 5",
                "date_arrivee": dt.date(2026, 9, 19),
                "date_depart": dt.date(2026, 9, 21),
                "statut": "parti",
                "consignataire": "Transit Sud",
            },
            {
                "navire": "MS Céleste",
                "type_navire": "passagers",
                "pavillon": "Espagne",
                "provenance": "Casablanca",
                "destination": "Dakar",
                "quai": "Terminal voyageurs",
                "date_arrivee": dt.date(2026, 9, 20),
                "date_depart": None,
                "statut": "a_quai",
                "consignataire": "Dakar Cruise",
            },
        ]

        created = 0
        for item in fixtures:
            _, is_new = Escale.objects.get_or_create(navire=item["navire"], defaults=item)
            if is_new:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} escales créées."))
