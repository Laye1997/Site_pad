"""Service applicatif des marchés publics (interface stable pour les autres apps)."""

from django.utils import timezone

from apps.marches.models import AppelOffre


def featured_tender():
    """Appel d'offres ouvert le plus récent (bandeau « Faire des affaires au port »)."""
    today = timezone.now().date()
    tenders = AppelOffre.objects.filter(statut="ouvert", type_marche="appel_offres")
    return (
        tenders.filter(date_limite__gte=today).order_by("date_limite").first()
        or tenders.order_by("-date_publication").first()
    )


def tender_counts() -> dict[str, int]:
    """Nombre de publications par type, pour les raccourcis de l'accueil."""
    return {
        code: AppelOffre.objects.filter(type_marche=code).count()
        for code, _ in AppelOffre.TYPE_CHOICES
    }
