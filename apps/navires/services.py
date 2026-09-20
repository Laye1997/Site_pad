"""Service applicatif du mouvement des navires (interface stable pour les autres apps)."""

from django.db.models import Max

from apps.navires.models import Escale


def movement_summary(limit: int = 5) -> dict:
    """Résumé du trafic : compteurs par statut, prochaines escales, date de mise à jour."""
    return {
        "attendus": Escale.objects.filter(statut="attendu").count(),
        "a_quai": Escale.objects.filter(statut="a_quai").count(),
        "partis": Escale.objects.filter(statut="parti").count(),
        "prochaines": list(
            Escale.objects.filter(statut__in=["attendu", "a_quai"]).order_by(
                "date_arrivee", "navire"
            )[:limit]
        ),
        "updated_at": Escale.objects.aggregate(last=Max("updated_at"))["last"],
    }


def list_escales(statut: str | None = None) -> list[Escale]:
    """Escales, filtrables par statut (attendu, a_quai, parti), pour l'API et les intégrations."""
    escales = Escale.objects.order_by("date_arrivee", "navire")
    if statut in {code for code, _ in Escale.STATUT_CHOICES}:
        escales = escales.filter(statut=statut)
    return list(escales)
