"""Crée l'article « Le Port Autonome de Dakar accueille le navire-hôpital chinois ».

Le port n'avait pas encore publié sur son propre site au moment de la rédaction ; le texte
reprend les faits rapportés par la presse sénégalaise (Terangatimes, Senego, Seneweb/DIRPA) le
25-26 septembre 2026, avec la mention du Directeur général du PAD. Photos : Senego, 25/09/2026.
Idempotent. Nécessite la page « Espace média » (commande seed_site_structure).
"""

import datetime as dt
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from wagtail.images.models import Image
from wagtail.rich_text import RichText

from apps.media.models import ArticlePage, MediaIndexPage

SOURCE = Path(settings.FRONTEND_DIR) / "static" / "img" / "origine"
TITLE = "Le Port Autonome de Dakar accueille le navire-hôpital chinois « Ji Xiang Fang Zhou »"

SUMMARY = (
    "Le navire-hôpital de la marine chinoise « Ji Xiang Fang Zhou » a accosté au Port Autonome "
    "de Dakar le vendredi 25 septembre 2026, une première escale de ce type au Sénégal, avec un "
    "programme de consultations médicales gratuites jusqu'au 1er octobre."
)

PARAGRAPHS = [
    "Le vendredi 25 septembre 2026, le Port Autonome de Dakar (PAD) a accueilli le navire-hôpital "
    "de la marine chinoise « Ji Xiang Fang Zhou », dans le cadre du renforcement de la "
    "coopération maritime et militaire entre le Sénégal et la Chine. Il s'agit de la première "
    "escale d'un navire-hôpital de la marine chinoise au Sénégal.",
    "Le bâtiment a été accueilli par des autorités de la Marine nationale sénégalaise et des "
    "représentants du Port Autonome de Dakar, dont le Directeur général, Doune Pathé Mbengue.",
    "Durant son escale, du 25 septembre au 1er octobre 2026, l'équipage médical du navire propose "
    "environ 600 consultations et soins spécialisés gratuits par jour aux populations "
    "sénégalaises, pour des patients déjà identifiés par les services compétents du ministère de "
    "la Santé. Les consultations se tiennent chaque jour jusqu'au 29 septembre ; la matinée du "
    "30 septembre est réservée aux soins déjà programmés.",
    "Le port a annoncé son plein appui opérationnel et logistique pour la réussite et la "
    "sécurité de cette campagne, menée en coordination avec les autorités sanitaires, la Marine "
    "nationale et l'ambassade de Chine au Sénégal.",
]

# (fichier, légende, texte alternatif) — la première photo sert d'image principale.
PHOTOS = [
    (
        "navire-hopital-chinois-1.jpg",
        "",
        "Le navire-hôpital militaire chinois « Ji Xiang Fang Zhou », marqué d'une grande croix "
        "rouge, amarré à quai au Port Autonome de Dakar.",
    ),
    (
        "navire-hopital-chinois-2.jpg",
        "La délégation accueillie par une foule agitant les drapeaux du Sénégal et de la Chine.",
        "Des officiers de la marine chinoise et des autorités sénégalaises en tenue blanche "
        "marchent au milieu d'une foule brandissant des drapeaux sénégalais et chinois.",
    ),
    (
        "navire-hopital-chinois-3.jpg",
        "Des marins sénégalais au garde-à-vous lors de la cérémonie d'accueil.",
        "Une rangée de marins sénégalais en tenue blanche, au garde-à-vous face au navire-hôpital "
        "chinois amarré au quai.",
    ),
    (
        "navire-hopital-chinois-4.jpg",
        "Le « Ji Xiang Fang Zhou », immatriculé 868, à quai au port de Dakar.",
        "Vue rapprochée de la coque blanche du navire-hôpital, portant le numéro 868 et une "
        "grande croix rouge.",
    ),
]


class Command(BaseCommand):
    help = "Crée l'article sur l'escale du navire-hôpital chinois « Ji Xiang Fang Zhou »."

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
            summary=SUMMARY,
            category="actualite",
            publication_date=dt.date(2026, 9, 25),
            cover_image=images[0],
            cover_alt=PHOTOS[0][2],
            body=body,
        )
        index.add_child(instance=article)
        article.save_revision().publish()
        self.stdout.write(f"Article créé : {article.url}")

    @staticmethod
    def _image(filename: str, title_prefix: str) -> Image:
        with (SOURCE / filename).open("rb") as handle:
            image = Image(title=f"{title_prefix} — {filename}")
            image.file.save(filename, File(handle), save=False)
            image.save()
        return image
