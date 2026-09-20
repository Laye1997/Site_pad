"""Met une photo sur chacune des 4 cases de l'offre de service (accueil).

Baliseur, Gorée, signature de dossiers d'agrément, chargement de marchandises.
Ne touche à aucune autre section ni aux autres cases. Idempotent.
"""

from django.core.management.base import BaseCommand

from apps.cms.home_blocks import (
    AGREMENT_FILE,
    AGREMENT_TITLE,
    BALISEUR_FILE,
    BALISEUR_TITLE,
    GOREE_FILE,
    GOREE_TITLE,
    MARCHANDISES_FILE,
    MARCHANDISES_TITLE,
    HomeSectionsBlock,
    library_image_id,
)
from apps.cms.models import HomePage

# (position, libellé, chemin de la page, fichier statique, titre dans la médiathèque)
TILES = [
    (
        0,
        "Accès nautique et balisage",
        "nos-services/acces-nautique-et-balisage",
        BALISEUR_FILE,
        BALISEUR_TITLE,
    ),
    (1, "Trafic passagers", "nos-services/trafic-passagers", GOREE_FILE, GOREE_TITLE),
    (
        2,
        "Obtenir un agrément",
        "opportunites-affaires/procedures-agrements/obtenir-un-agrement",
        AGREMENT_FILE,
        AGREMENT_TITLE,
    ),
    (3, "Marchandises", "nos-services/marchandises", MARCHANDISES_FILE, MARCHANDISES_TITLE),
]


class Command(BaseCommand):
    help = "Met à jour les photos des cases de l'offre de service sur l'accueil."

    def handle(self, *args, **options):
        images = {
            pos: library_image_id(file, title) if file else None for pos, _, _, file, title in TILES
        }
        for home in HomePage.objects.all():
            raw = [
                {"type": b.block_type, "value": b.block.get_prep_value(b.value)}
                for b in home.sections
            ]
            changed = False
            for section in raw:
                if section["type"] != "service_band":
                    continue
                services = section["value"]["services"]
                for pos, label, path, _file, _title in TILES:
                    if pos >= len(services):
                        continue
                    entry = services[pos]
                    item = entry["value"] if "value" in entry else entry
                    wanted = {"label": label, "url_path": path, "page": None}
                    if images[pos] is not None:
                        wanted["image"] = images[pos]
                    if all(item.get(k) == v for k, v in wanted.items()):
                        continue
                    item.update(wanted)
                    changed = True
            if not changed:
                self.stdout.write(f"{home.title} : rien à changer.")
                continue
            home.sections = HomeSectionsBlock().to_python(raw)
            home.save_revision().publish()
            self.stdout.write(f"{home.title} : offre de service mise à jour.")
