"""Service applicatif des certifications (interface stable pour les autres apps)."""

from datetime import timedelta

from django.utils import timezone

from apps.qualite.models import Certification


def valid_certifications():
    """Certifications en cours de validité — jamais un certificat périmé."""
    return list(
        Certification.objects.filter(date_validite__gte=timezone.now().date()).select_related(
            "visual", "document"
        )
    )


def expiring_certifications(days: int = 90):
    """Certifications valides qui expirent dans `days` jours (alerte aux administrateurs)."""
    today = timezone.now().date()
    limit = today + timedelta(days=days)
    return list(Certification.objects.filter(date_validite__gte=today, date_validite__lte=limit))
