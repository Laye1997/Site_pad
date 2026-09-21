"""Ajoute les deux photos de l'ancien site à la page « Accès nautique et balisage ».

- le baliseur « Samba Laobé Fall » après le paragraphe d'introduction ;
- le chargement d'une bouée à la fin de la page.
Idempotent : ne fait rien si les photos sont déjà présentes.
"""

from django.core.management.base import BaseCommand

from apps.cms.home_blocks import BALISEUR_FILE, BALISEUR_TITLE, library_image_id
from apps.core.blocks import ContentStreamBlock
from apps.services.models import ServicePage

SLUG = "acces-nautique-et-balisage"
BALISEUR_ALT = (
    "Le baliseur Samba Laobé Fall en mer, navire de la Subdivision des Phares et Balises."
)
BOUEE_TITLE = "Chargement d'une bouée sur le baliseur"
BOUEE_ALT = (
    "Une bouée rouge est levée par la grue du baliseur sur le quai, "
    "au milieu de chaînes d'ancrage et de l'équipage."
)


def apply_nautique_images(page) -> bool:
    """Insère les photos dans le corps de la page. Retourne True si la page a été modifiée."""
    raw = [{"type": b.block_type, "value": b.block.get_prep_value(b.value)} for b in page.body]
    known = {block["value"].get("alt") for block in raw if block["type"] == "image"}
    baliseur_id = library_image_id(BALISEUR_FILE, BALISEUR_TITLE)
    bouee_id = library_image_id("origine/image2.png", BOUEE_TITLE)
    changed = False
    if BOUEE_ALT not in known and bouee_id:
        raw.append({"type": "image", "value": {"image": bouee_id, "caption": "", "alt": BOUEE_ALT}})
        changed = True
    if BALISEUR_ALT not in known and baliseur_id:
        position = next((i + 1 for i, b in enumerate(raw) if b["type"] == "paragraph"), 0)
        raw.insert(
            position,
            {"type": "image", "value": {"image": baliseur_id, "caption": "", "alt": BALISEUR_ALT}},
        )
        changed = True
    if changed:
        page.body = ContentStreamBlock().to_python(raw)
        page.save_revision().publish()
    return changed


class Command(BaseCommand):
    help = "Ajoute les photos du baliseur et de la bouée à la page Accès nautique et balisage."

    def handle(self, *args, **options):
        pages = ServicePage.objects.filter(slug=SLUG)
        if not pages:
            self.stdout.write("Page introuvable : lancez seed_site_structure.")
            return
        for page in pages:
            state = "photos ajoutées" if apply_nautique_images(page) else "déjà à jour"
            self.stdout.write(f"{page.title} : {state}.")
