"""Copie la composition par défaut de l'accueil dans la page, pour la rendre modifiable.

Sans effet sur une page qui a déjà des sections (utiliser --force pour les remplacer).
"""

from django.core.management.base import BaseCommand
from wagtail.models import Site

from apps.cms.home_blocks import HomeSectionsBlock, default_home_sections
from apps.cms.models import HomePage


class Command(BaseCommand):
    help = "Enregistre la composition par défaut de l'accueil (sections modifiables)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="Remplace les sections existantes."
        )

    def handle(self, *args, force: bool, **options):
        site = Site.objects.filter(is_default_site=True).first()
        homes = HomePage.objects.all()
        if site is not None:
            homes = homes.filter(pk=site.root_page_id) or homes
        for home in homes:
            if len(home.sections) and not force:
                self.stdout.write(f"{home.title} : sections déjà définies, ignoré.")
                continue
            raw = [{"type": kind, "value": value} for kind, value in default_home_sections(home)]
            home.sections = HomeSectionsBlock().to_python(raw)
            home.save_revision().publish()
            self.stdout.write(f"{home.title} : {len(raw)} sections enregistrées.")
