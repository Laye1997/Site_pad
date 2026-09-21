"""Pose une vraie photo (ancien site) sur la carte de chaque rubrique de l'accueil.

Ne remplace jamais une photo déjà choisie par un rédacteur. Idempotent.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Site

from apps.cms.home_blocks import library_image_id

# slug de la rubrique -> (fichier statique, titre dans la médiathèque)
PHOTOS = {
    "nous-decouvrir": ("origine/installation_0.jpg", "Vue aérienne du port de Dakar"),
    "nos-services": ("origine/terminal_a_conteneur2.jpg", "Terminal à conteneurs du port"),
    "opportunites-affaires": ("origine/platefprme.jpg", "Plateforme logistique du port"),
    "espace-media": (
        "origine/564966186_17986931567902890_5511344601655925438_n.jpg",
        "Visite de la maquette du port",
    ),
    "infos-pratiques": ("origine/mapppad.jpg", "Carte des lignes maritimes"),
    "engagements": (
        "origine/564759173_17986931708902890_2584020602956053619_n.jpg",
        "Côte de Dakar, environnement",
    ),
    "espace-pro-recrutement": ("origine/dsc_0958.jpg", "Salle de contrôle du port"),
}


class Command(BaseCommand):
    help = "Met une photo sur les cartes de rubriques de l'accueil."

    def handle(self, *args, **options):
        done = 0
        root = Site.objects.get(is_default_site=True).root_page
        for slug, (filename, title) in PHOTOS.items():
            page = root.get_children().filter(slug=slug).specific().first()
            if page is None or not hasattr(page, "card_image") or page.card_image_id:
                continue
            image_id = library_image_id(filename, title)
            if image_id is None:
                continue
            page.card_image_id = image_id
            page.save_revision().publish()
            done += 1
        self.stdout.write(f"{done} rubrique(s) illustrée(s).")
