"""Liste les certifications arrivant à échéance prochainement."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.qualite.models import Certification


class Command(BaseCommand):
    help = "Liste les certifications expirant dans moins de 60 jours."

    def handle(self, *args, **options):
        today = timezone.now().date()
        limit = today + timedelta(days=60)
        certifications = Certification.objects.filter(
            date_validite__gte=today, date_validite__lte=limit
        )
        if not certifications.exists():
            self.stdout.write("Aucune certification n'expire dans les 60 prochains jours.")
            return
        for certification in certifications:
            self.stdout.write(
                f"{certification.get_referentiel_display()} — "
                f"{certification.date_validite.isoformat()}"
            )
