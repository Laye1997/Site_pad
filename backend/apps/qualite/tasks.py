"""Tâches de fond de l'app qualité."""

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from apps.qualite.services import expiring_certifications


def _recipients() -> list[str]:
    configured = list(settings.CERTIFICATION_ALERT_EMAILS)
    if configured:
        return configured
    return list(
        get_user_model()
        .objects.filter(is_superuser=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


@shared_task
def alert_expiring_certifications() -> int:
    """Prévient les administrateurs des certifications qui expirent bientôt.

    Retourne le nombre de certificats signalés (0 : aucun e-mail envoyé).
    """
    days = settings.CERTIFICATION_ALERT_DAYS
    certifications = expiring_certifications(days)
    recipients = _recipients()
    if not certifications or not recipients:
        return 0
    lines = [
        f"- {cert.get_referentiel_display()} : valide jusqu'au {cert.date_validite:%d/%m/%Y}"
        for cert in certifications
    ]
    send_mail(
        subject=f"[PAD] {len(certifications)} certification(s) expirent dans moins de {days} jours",
        message="Certifications à renouveler :\n\n" + "\n".join(lines),
        from_email=None,
        recipient_list=recipients,
    )
    return len(certifications)
