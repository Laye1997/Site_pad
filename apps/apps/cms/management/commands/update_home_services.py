"""Met une photo sur chacune des 4 cases de l'offre de service (accueil).

Baliseur, Gorée, signature de dossiers d'agrément, chargement de marchandises.
Ne touche à aucune autre section ni aux autres cases. Idempotent.
"""

import uuid

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
    MOVEMENT_TILES,
    HomeSectionsBlock,
    default_home_sections,
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
            if raw and not any(section["type"] == "service_band" for section in raw):
                # Page créée avant cette section : on l'ajoute juste après les actualités.
                kind, value = next(
                    (k, v) for k, v in default_home_sections(home) if k == "service_band"
                )
                built = HomeSectionsBlock().to_python([{"type": kind, "value": value}])
                new = {"type": kind, "value": built[0].block.get_prep_value(built[0].value)}
                types = [section["type"] for section in raw]
                raw.insert(types.index("news") + 1 if "news" in types else len(raw), new)
                changed = True
                self.stdout.write(f"{home.title} : section « Offre de service » ajoutée.")
            for section in raw:
                if section["type"] != "service_band":
                    continue
                if not section["value"].get("show_movement"):
                    section["value"]["show_movement"] = True
                    changed = True
                if self._movement_links(section["value"]):
                    changed = True
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

    @staticmethod
    def _movement_links(value) -> bool:
        """Cases du mouvement des navires : posées si absentes, sans écraser celles de l'éditeur."""
        existing = [
            (entry.get("value", entry) if isinstance(entry, dict) else {})
            for entry in value.get("movement_links") or []
        ]
        if any(item.get("url_path") or item.get("page") for item in existing):
            return False
        value["movement_links"] = [
            {
                "type": "item",
                "id": str(uuid.uuid4()),
                "value": {
                    "label": label,
                    "icon": "ship",
                    "page": None,
                    "url_path": path,
                    "image": library_image_id(file, title),
                },
            }
            for label, path, file, title in MOVEMENT_TILES
        ]
        return True
