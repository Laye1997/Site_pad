"""Envoie l'alerte d'expiration des certifications (utilisable en cron sans Celery)."""

from django.core.management.base import BaseCommand

from apps.qualite.tasks import alert_expiring_certifications


class Command(BaseCommand):
    help = "Prévient les administrateurs des certifications ISO proches de l'expiration."

    def handle(self, *args, **options):
        count = alert_expiring_certifications()
        self.stdout.write(f"{count} certification(s) signalée(s).")
