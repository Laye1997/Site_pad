"""Crée des contenus DE DÉMONSTRATION pour l'espace média (à supprimer avant la mise en ligne).

- Notes aux usagers : titres relevés sur l'accueil de l'ancien site.
- Actualités : titres génériques préfixés « [Démo] », illustrés par des photos de l'ancien site.
Idempotent. Nécessite la page « Espace média » (commande seed_site_structure).
"""

import datetime as dt
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from wagtail.images.models import Image

from apps.media.models import ArticlePage, MediaIndexPage

SOURCE = Path(settings.FRONTEND_DIR) / "static" / "img" / "origine"

NOTICES = [
    (
        "Avis de signature : projet de terminal à conteneurs du Port de Ndayane",
        "Dans le cadre du projet de réalisation du terminal à conteneurs du Port de Ndayane, "
        "les documents suivants ont été signés.",
    ),
    ("Note d'information", "Note d'information à l'attention des usagers du port."),
    (
        "Note circulaire : comité ad hoc de suivi des marchandises en souffrance",
        "Mise en place du comité ad hoc de suivi des marchandises en souffrance au Port de Dakar.",
    ),
    (
        "Échange électronique des Bons à Délivrer (BAD) dès le 2 janvier 2026",
        "Le Port Autonome de Dakar et la Direction Générale des Douanes sénégalaises annoncent "
        "le lancement de la phase pilote de l'échange électronique des BAD.",
    ),
]

NEWS: list[tuple[str, str, str]] = []  # actualités démo retirées : voir seed_passation_article


class Command(BaseCommand):
    help = "Crée des actualités et notes aux usagers de démonstration (idempotent)."

    def handle(self, *args, **options):
        index = MediaIndexPage.objects.first()
        if index is None:
            raise CommandError("Page « Espace média » introuvable : lancez seed_site_structure.")
        today = dt.date.today()
        created = 0
        for offset, (title, summary) in enumerate(NOTICES):
            created += self._article(
                index, title, summary, "note", today - dt.timedelta(days=offset * 6), None
            )
        for offset, (category, title, filename) in enumerate(NEWS):
            summary = "Contenu de démonstration : à remplacer par une publication officielle."
            created += self._article(
                index, title, summary, category, today - dt.timedelta(days=offset * 4), filename
            )
        self.stdout.write(f"{created} article(s) de démonstration créé(s).")

    def _article(self, index, title, summary, category, date, filename):
        if ArticlePage.objects.filter(title=title).exists():
            return 0
        image = None
        path = SOURCE / filename if filename else None
        if path and path.exists():
            with path.open("rb") as handle:
                image = Image(title=title)
                image.file.save(filename, File(handle), save=False)
                image.save()
        article = ArticlePage(
            title=title,
            summary=summary,
            category=category,
            publication_date=date,
            cover_image=image,
            cover_alt="Photo d'illustration du Port Autonome de Dakar" if image else "",
        )
        index.add_child(instance=article)
        article.save_revision().publish()
        return 1
