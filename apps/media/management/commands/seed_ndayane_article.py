"""Crée l'article « Port de Ndayane : DP World confirme la livraison au troisième trimestre 2028 ».

Texte fourni par le PAD (publication du 17 septembre 2026, reprise du post Facebook).
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

SOURCE = Path(settings.BASE_DIR) / "static" / "img" / "origine"
TITLE = "Port de Ndayane : DP World confirme la livraison au troisième trimestre 2028"

SUMMARY = (
    "Le Premier ministre, Ahmadou Al Aminou LÔ, a reçu Mohammed AKOJEE, Directeur Afrique de "
    "DP World, pour faire le point sur l'avancement du futur Port de Ndayane. Le Directeur "
    "Général du PAD, Doune Pathé Mbengue, a pris part aux échanges."
)

PARAGRAPHS = [
    "Ce jeudi 17 septembre 2026, le Premier ministre, Ahmadou Al Aminou LÔ, a reçu Mohammed "
    "AKOJEE, Directeur Afrique de DP World, pour faire le point sur l'état d'avancement du "
    "futur Port de Ndayane.",
    "Le Directeur Général du Port Autonome de Dakar, Doune Pathé Mbengue, a activement pris "
    "part aux échanges.",
    "Le groupe émirati a réitéré son engagement à respecter les délais impartis, confirmant la "
    "mise à disposition de cette infrastructure portuaire de premier plan d'ici l'été 2028.",
    "Une étape clé pour la modernisation de l'écosystème maritime sénégalais, portée par la "
    "nouvelle direction du PAD.",
]

PHOTOS = [
    (
        "ndayane-dp-world-1.jpg",
        "Poignée de main entre deux hommes en costume dans un bureau.",
    ),
    (
        "ndayane-dp-world-2.jpg",
        "Réunion autour d'une grande table de conférence, le drapeau du Sénégal en arrière-plan.",
    ),
    (
        "ndayane-dp-world-3.jpg",
        "Les participants à la réunion, assis autour de la table, face aux baies vitrées.",
    ),
]


class Command(BaseCommand):
    help = "Crée l'article Ndayane / DP World du 17 septembre 2026 (idempotent)."

    def handle(self, *args, **options):
        index = MediaIndexPage.objects.first()
        if index is None:
            raise CommandError("Page « Espace média » introuvable : lancez seed_site_structure.")
        if ArticlePage.objects.filter(title=TITLE).exists():
            self.stdout.write("Article déjà présent.")
            return
        images = []
        for filename, _ in PHOTOS:
            with (SOURCE / filename).open("rb") as handle:
                image = Image(title=f"Ndayane DP World — {filename}")
                image.file.save(filename, File(handle), save=False)
                image.save()
            images.append(image)
        body = [("paragraph", RichText(f"<p>{text}</p>")) for text in PARAGRAPHS]
        for image, (_, alt) in zip(images[1:], PHOTOS[1:], strict=True):
            body.append(("image", {"image": image, "caption": "", "alt": alt}))
        article = ArticlePage(
            title=TITLE,
            summary=SUMMARY,
            category="actualite",
            publication_date=dt.date(2026, 9, 17),
            cover_image=images[0],
            cover_alt=PHOTOS[0][1],
            body=body,
        )
        index.add_child(instance=article)
        article.save_revision().publish()
        self.stdout.write(f"Article créé : {article.url}")
