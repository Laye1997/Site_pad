"""Importe les deux certificats AFNOR de l'ancien site (aperçus + données lisibles sur les scans).

Idempotent. Les données (n°, dates) sont relevées sur les scans : à vérifier par la Qualité.
"""

from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from apps.qualite.models import Certification

SOURCE = Path(settings.BASE_DIR) / "static" / "img" / "origine"

CERTIFICATES = [
    {
        "file": "certificat_iso_9001_pad_2027.png",
        "referentiel": "iso9001",
        "perimetre": "SONAPAD — Direction Générale et Haut commandement du Port : aménagement, "
        "gestion et exploitation du domaine portuaire, services aux navires, aux passagers, "
        "aux marchandises et aux usagers",
        "numero": "2006/26390.8",
        "date_emission": date(2024, 3, 21),
    },
    {
        "file": "certificat_qse_gmidzone_sud_2027.png",
        "referentiel": "iso14001",
        "perimetre": "Gare maritime internationale de Dakar et zone Sud (GMID) — ISO 9001, "
        "ISO 14001 et ISO 45001 : services aux navires, aux marchandises et aux passagers",
        "numero": "2019/82088.5",
        "date_emission": date(2024, 3, 16),
    },
]


class Command(BaseCommand):
    help = "Importe les certificats AFNOR de l'ancien site (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for item in CERTIFICATES:
            if Certification.objects.filter(numero=item["numero"]).exists():
                continue
            path = SOURCE / item["file"]
            image = None
            if path.exists():
                with path.open("rb") as handle:
                    image = Image(title=f"Certificat {item['numero']}")
                    image.file.save(item["file"], File(handle), save=False)
                    image.save()
            Certification.objects.create(
                referentiel=item["referentiel"],
                perimetre=item["perimetre"],
                organisme="AFNOR Certification",
                numero=item["numero"],
                date_emission=item["date_emission"],
                date_validite=date(2027, 2, 10),
                visual=image,
            )
            created += 1
        self.stdout.write(f"{created} certificat(s) importé(s).")
