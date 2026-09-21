"""Crée des exemples de marchés publics."""

import datetime as dt

from django.core.management.base import BaseCommand

from apps.marches.models import AppelOffre


class Command(BaseCommand):
    help = "Crée des exemples de marchés publics."

    def handle(self, *args, **options):
        fixtures = [
            {
                "reference": "PAD-AO-2026-001",
                "objet": "Travaux de maintenance du terminal à conteneurs",
                "type_marche": "appel_offres",
                "date_publication": dt.date(2026, 9, 5),
                "date_limite": dt.date(2026, 10, 5),
                "statut": "ouvert",
            },
            {
                "reference": "PAD-AT-2026-004",
                "objet": "Fourniture de matériels de sécurité portuaire",
                "type_marche": "avis_attribution",
                "date_publication": dt.date(2026, 8, 22),
                "date_limite": None,
                "statut": "attribue",
            },
            {
                "reference": "PAD-PP-2027",
                "objet": "Plan prévisionnel des marchés 2027",
                "type_marche": "plan_passation",
                "date_publication": dt.date(2026, 9, 1),
                "date_limite": None,
                "statut": "cloture",
            },
        ]

        created = 0
        for item in fixtures:
            _, is_new = AppelOffre.objects.get_or_create(
                reference=item["reference"],
                defaults=item,
            )
            if is_new:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} marchés créés."))
