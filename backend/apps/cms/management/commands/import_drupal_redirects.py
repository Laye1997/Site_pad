"""Importe les redirections permanentes des anciennes URL Drupal 7 (/node/, /content/, /viewpdf).

Format du CSV (UTF-8, séparateur virgule, avec en-tête) :

    ancienne_url,nouvelle_page
    /fr/node/123,nous-decouvrir/presentation/historique
    /fr/content/pilotage,nos-services/pilotage

`nouvelle_page` est le chemin de slugs de la page Wagtail cible (sans langue) ; une URL
absolue ou commençant par « / » est aussi acceptée. Les lignes déjà importées sont ignorées.
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site


class Command(BaseCommand):
    help = "Importe des redirections 301 depuis un fichier CSV (ancienne_url,nouvelle_page)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=Path)
        parser.add_argument("--dry-run", action="store_true", help="Affiche sans écrire.")

    def handle(self, *args, csv_path: Path, dry_run: bool, **options):
        if not csv_path.exists():
            raise CommandError(f"Fichier introuvable : {csv_path}")
        site = Site.objects.get(is_default_site=True)
        created = skipped = missing = 0
        with csv_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                old_path = (row.get("ancienne_url") or "").strip()
                target = (row.get("nouvelle_page") or "").strip()
                if not old_path or not target:
                    continue
                if not old_path.startswith("/"):
                    old_path = "/" + old_path
                normalised = Redirect.normalise_path(old_path)
                if Redirect.objects.filter(site=site, old_path=normalised).exists():
                    skipped += 1
                    continue
                page = None
                if not target.startswith(("/", "http")):
                    page = self._find_page(site, target)
                    if page is None:
                        missing += 1
                        self.stderr.write(f"Page cible introuvable : {target} (pour {old_path})")
                        continue
                if dry_run:
                    self.stdout.write(f"{old_path} -> {page.url if page else target}")
                else:
                    Redirect.objects.create(
                        site=site,
                        old_path=old_path,
                        is_permanent=True,
                        redirect_page=page,
                        redirect_link="" if page else target,
                    )
                created += 1
        self.stdout.write(f"{created} créée(s), {skipped} déjà présente(s), {missing} sans cible.")

    @staticmethod
    def _find_page(site, path):
        page = site.root_page
        for slug in path.strip("/").split("/"):
            page = page.get_children().filter(slug=slug).first()
            if page is None:
                return None
        return page
