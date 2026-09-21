"""Importe les logos de partenaires de l'ancien site (static/img/origine) comme snippets Partner.

Les noms sont déduits des fichiers : à relire et corriger dans l'admin (Snippets > Partenaires).
La commande est idempotente (un partenaire existant n'est pas recréé).
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from apps.cms.models import Partner

SOURCE = Path(settings.FRONTEND_DIR) / "static" / "img" / "origine"

# fichier -> nom affiché
LOGOS = {
    "maersk.jpg": "Maersk",
    "bollore_logistic.jpg": "Bolloré Logistics",
    "getma.png": "GETMA",
    "grimaldi_group_0.jpg": "Grimaldi Group",
    "dp_word.png": "DP World",
    "necotrans_0.jpg": "Necotrans",
    "sntt_logistics.jpg": "SNTT Logistics",
    "vivo_energy.jpg": "Vivo Energy",
    "sococim_1.jpg": "Sococim",
    "ciments_du_sahel.jpg": "Ciments du Sahel",
    "grands_moulins.jpg": "Grands Moulins de Dakar",
    "ics.png": "ICS",
    "sar_0.jpg": "SAR",
    "senelec.png": "Senelec",
    "sde.png": "SDE",
    "sonatel_0.jpg": "Sonatel",
    "la_poste.jpg": "La Poste",
    "douane.jpg": "Douane sénégalaise",
    "anam_0.jpg": "ANAM",
    "apix_0.jpg": "APIX",
    "cnp_0.jpg": "CNP",
    "ones.png": "ONES",
    "cciad.png": "CCIAD",
    "unacois_jappo.jpg": "UNACOIS Jappo",
    "fenagie_peche.jpg": "FENAGIE Pêche",
    "chambre_des_notaires.jpg": "Chambre des notaires du Sénégal",
    "ministere_de_lindustrie_et_du_commerce.png": "Ministère de l'Industrie et du Commerce",
    "ministere_interieur_et_securite_public.png": (
        "Ministère de l'Intérieur et de la Sécurité publique"
    ),
    "dunkerque_0.jpg": "Port de Dunkerque",
    "autorita_portuale_di_genova.jpg": "Autorità di Sistema Portuale de Gênes",
    "puertos_de_las_palmas.png": "Puertos de Las Palmas",
    "port_miami_0.jpg": "PortMiami",
    "port_of_luisiane.jpg": "Port of South Louisiana",
    "cape_town.jpg": "Port du Cap",
    "port_de_lamitie.png": "Port de l'Amitié",
}


class Command(BaseCommand):
    help = "Importe les logos de partenaires de l'ancien site (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for filename, name in LOGOS.items():
            path = SOURCE / filename
            if not path.exists() or Partner.objects.filter(name=name).exists():
                continue
            with path.open("rb") as handle:
                image = Image(title=f"Logo {name}")
                image.file.save(filename, File(handle), save=False)
                image.save()
            Partner.objects.create(name=name, logo=image, position=created)
            created += 1
        self.stdout.write(f"{created} partenaire(s) importé(s).")
