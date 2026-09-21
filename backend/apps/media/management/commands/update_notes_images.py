"""Ajoute des photos aux notes aux usagers qui n'en ont pas (photos de l'ancien site).

- « Avis de signature : projet de terminal à conteneurs du Port de Ndayane » : photos de la
  cérémonie de signature. À CONFIRMER par la communication : elles viennent d'un même album de
  l'ancien site, non légendé.
Ne remplace jamais une image déjà renseignée. Idempotent.
"""

from django.core.management.base import BaseCommand

from apps.cms.home_blocks import library_image_id
from apps.core.blocks import ContentStreamBlock
from apps.media.models import ArticlePage

NDAYANE_TITLE_START = "Avis de signature"
COVER = (
    "origine/585584787_837931609191865_3920781033585031610_n.jpg",
    "Signature du terminal à conteneurs de Ndayane",
    "Des signataires en tenues traditionnelles paraphent des documents autour d'une grande table.",
)
BODY = [
    (
        "origine/585040766_837931519191874_3720178164644818917_n.jpg",
        "Cérémonie de signature — assemblée",
        "Les participants à la cérémonie de signature, assis autour d'une table de conférence.",
    ),
    (
        "origine/585886475_837931529191873_2095067578186340988_n.jpg",
        "Cérémonie de signature — salle",
        "La salle de la cérémonie, avec les représentants des institutions et des partenaires.",
    ),
    (
        "origine/586041961_837931829191843_139065525193150296_n.jpg",
        "Cérémonie de signature — photo de groupe",
        "Photo de groupe des responsables à l'issue de la cérémonie de signature.",
    ),
]


class Command(BaseCommand):
    help = "Ajoute les photos de la cérémonie de signature de Ndayane à la note correspondante."

    def handle(self, *args, **options):
        done = 0
        for article in ArticlePage.objects.filter(title__startswith=NDAYANE_TITLE_START):
            changed = False
            if not article.cover_image_id:
                cover_id = library_image_id(COVER[0], COVER[1])
                if cover_id:
                    article.cover_image_id = cover_id
                    article.cover_alt = COVER[2]
                    changed = True
            if not any(block.block_type == "image" for block in article.body):
                raw = [
                    {"type": b.block_type, "value": b.block.get_prep_value(b.value)}
                    for b in article.body
                ]
                for filename, title, alt in BODY:
                    image_id = library_image_id(filename, title)
                    if image_id:
                        raw.append(
                            {
                                "type": "image",
                                "value": {"image": image_id, "caption": "", "alt": alt},
                            }
                        )
                article.body = ContentStreamBlock().to_python(raw)
                changed = True
            if changed:
                article.save_revision().publish()
                done += 1
        self.stdout.write(f"{done} note(s) illustrée(s).")
