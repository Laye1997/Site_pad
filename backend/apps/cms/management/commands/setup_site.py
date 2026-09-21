"""Configure la racine du site : accueil, adresse publique, suppression de la page par défaut.

Idempotent. Usage :  python manage.py setup_site --host 102.203.220.55 --port 1515
- crée la page « Accueil » (HomePage) si elle n'existe pas ;
- déplace sous l'accueil les pages rangées sous la page « Welcome to your new Wagtail site! » ;
- supprime cette page par défaut, une fois vidée ;
- règle le Site Wagtail par défaut (adresse, port, racine = accueil).
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.cms.models import HomePage


class Command(BaseCommand):
    help = "Définit l'accueil comme racine du site et règle l'adresse publique."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="localhost")
        parser.add_argument("--port", type=int, default=80)

    def handle(self, *args, host: str, port: int, **options):
        root = Page.objects.get(depth=1)
        home = HomePage.objects.first()
        if home is None:
            home = HomePage(title="Accueil", slug="accueil")
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write("Page d'accueil créée.")
        moved = 0
        for other in Page.objects.filter(depth=2).exclude(pk=home.pk):
            while True:
                child = Page.objects.get(pk=other.pk).get_children().first()
                if child is None:
                    break
                child.move(Page.objects.get(pk=home.pk), pos="last-child")
                moved += 1
            Page.objects.get(pk=other.pk).delete()
            self.stdout.write(f"Page supprimée : {other.title}")
        site = Site.objects.filter(is_default_site=True).first() or Site(is_default_site=True)
        site.hostname = host
        site.port = port
        site.site_name = "Port Autonome de Dakar"
        site.root_page = Page.objects.get(pk=home.pk)
        site.save()
        self.stdout.write(f"{moved} page(s) déplacée(s). Site : {site} -> racine : {home.title}")
