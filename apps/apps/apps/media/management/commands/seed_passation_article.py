"""Reprend l'article « Passation de service au Port Autonome de Dakar » de l'ancien site.

Texte et photos proviennent de portdakar.sn (publié le 14 août 2026). Idempotent.
Nécessite la page « Espace média » (commande seed_site_structure).
"""

import datetime as dt
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from wagtail.images.models import Image
from wagtail.rich_text import RichText

from apps.media.models import ArticlePage, MediaIndexPage

SOURCE = Path(settings.BASE_DIR) / "static" / "img" / "origine"
TITLE = "Passation de service au Port Autonome de Dakar"

SUMMARY = (
    "Ce jeudi 13 août 2026, une page se tourne et une nouvelle s'ouvre à la Direction générale "
    "du Port Autonome de Dakar (PAD). Monsieur Waly Diouf BODIANG a officiellement transmis le "
    "témoin à Monsieur Doune Pathé MBENGUE, nouveau Directeur général."
)

PARAGRAPHS = [
    "Dans un contexte solennel, les deux dirigeants ont présenté des allocutions "
    "complémentaires partageant une vision commune : transformer Dakar en plateforme logistique "
    "moderne, performante et inclusive.",
    "Le nouveau directeur général a exprimé sa gratitude envers le Président de la République, "
    "Bassirou Diomaye Faye, pour la confiance manifestée. Il a réaffirmé son engagement à faire "
    "du PAD « un levier majeur de souveraineté et de croissance durable, en phase avec le "
    "référentiel Sénégal 2050. »",
    "Des félicitations ont été adressées au prédécesseur pour les progrès réalisés, tandis "
    "qu'un appel à la mobilisation collective a été lancé aux équipes afin de développer une "
    "infrastructure logistique et industrielle davantage compétitive et novatrice.",
]

# (fichier, légende, texte alternatif) — la première photo sert d'image principale.
PHOTOS = [
    (
        "whatsapp_image_2026-08-14_at_11.35.39_1.jpeg",
        "Les deux dirigeants lors de la cérémonie de passation de service.",
        "Deux hommes assis côte à côte devant un fond aux couleurs du Port Autonome de Dakar.",
    ),
    (
        "whatsapp_image_2026-08-14_at_11.35.40_4.jpeg",
        "Remise d'un présent lors de la cérémonie.",
        "Deux hommes se serrent la main devant un fond du Port Autonome de Dakar, "
        "l'un tenant un présent emballé.",
    ),
    (
        "whatsapp_image_2026-08-14_at_11.35.41_2.jpeg",
        "Un portrait dédicacé du Directeur général sortant.",
        "Des membres du personnel présentent un cadre-portrait signé par les agents du port.",
    ),
    (
        "whatsapp_image_2026-08-14_at_11.35.41_3.jpeg",
        "Les autorités et les partenaires du port dans la salle.",
        "Des responsables et des représentants d'institutions assis autour d'une table.",
    ),
    (
        "whatsapp_image_2026-08-14_at_11.35.42_1.jpeg",
        "Les agents du port réunis pour la cérémonie.",
        "Une assemblée de personnel du Port Autonome de Dakar assise dans une salle.",
    ),
]


class Command(BaseCommand):
    help = "Crée l'article « Passation de service » repris de l'ancien site (idempotent)."

    def handle(self, *args, **options):
        index = MediaIndexPage.objects.first()
        if index is None:
            raise CommandError("Page « Espace média » introuvable : lancez seed_site_structure.")
        if ArticlePage.objects.filter(title=TITLE).exists():
            self.stdout.write("Article déjà présent.")
            return
        images = [self._image(name, TITLE) for name, _, _ in PHOTOS]
        body = [("paragraph", RichText(f"<p>{text}</p>")) for text in PARAGRAPHS]
        for image, (_, caption, alt) in zip(images[1:], PHOTOS[1:], strict=True):
            body.append(("image", {"image": image, "caption": caption, "alt": alt}))
        article = ArticlePage(
            title=TITLE,
            slug="passation-de-service-au-port-autonome-de-dakar",
            summary=SUMMARY,
            category="actualite",
            publication_date=dt.date(2026, 8, 14),
            cover_image=images[0],
            cover_alt=PHOTOS[0][2],
            body=body,
        )
        index.add_child(instance=article)
        article.save_revision().publish()
        self.stdout.write(f"Article créé : {article.url}")

    @staticmethod
    def _image(filename, title):
        with (SOURCE / filename).open("rb") as handle:
            image = Image(title=f"{title} — {filename[-15:-5]}")
            image.file.save(filename, File(handle), save=False)
            image.save()
        return image
