"""Vues publiques du mouvement des navires."""

from django.db.models import Count, Max, Q
from django.shortcuts import render

from apps.navires.models import Escale

FILTRES = {
    "arrivees": {
        "label": "Arrivées",
        "query": Q(statut__in=["attendu", "a_quai"]),
    },
    "a_quai": {
        "label": "À quai",
        "query": Q(statut="a_quai"),
    },
    "departs": {
        "label": "Départs",
        "query": Q(statut="parti"),
    },
}


# Bilan croisière publié par le PAD (publication « Performance : escale de référence », 2025).
BILAN_CROISIERE = [
    {"annee": "2023", "navires": 24, "passagers": "12 771"},
    {"annee": "2024", "navires": 31, "passagers": "17 850"},
    {"annee": "2025 (juin)", "navires": 29, "passagers": "15 554"},
]


def _counts() -> dict[str, int]:
    """Nombre d'escales par onglet, en une seule requête."""
    by_status = dict(Escale.objects.values_list("statut").annotate(n=Count("pk")))
    return {
        "arrivees": by_status.get("attendu", 0) + by_status.get("a_quai", 0),
        "a_quai": by_status.get("a_quai", 0),
        "departs": by_status.get("parti", 0),
        "attendus": by_status.get("attendu", 0),
    }


def escale_list(request):
    """Tableau de bord des escales : onglets, recherche, type de navire, mise à jour HTMX."""
    filtre = request.GET.get("filtre", "arrivees")
    filtre_actif = filtre if filtre in FILTRES else "arrivees"
    recherche = request.GET.get("q", "").strip()[:80]
    type_navire = request.GET.get("type", "")
    if type_navire not in dict(Escale.TYPE_CHOICES):
        type_navire = ""

    queryset = Escale.objects.filter(FILTRES[filtre_actif]["query"])
    if recherche:
        queryset = queryset.filter(
            Q(navire__icontains=recherche)
            | Q(provenance__icontains=recherche)
            | Q(destination__icontains=recherche)
            | Q(consignataire__icontains=recherche)
            | Q(pavillon__icontains=recherche)
        )
    if type_navire:
        queryset = queryset.filter(type_navire=type_navire)
    queryset = queryset.order_by("date_arrivee", "navire")

    counts = _counts()
    context = {
        "escales": queryset,
        "filtre_actif": filtre_actif,
        "filtres": {key: {**config, "count": counts[key]} for key, config in FILTRES.items()},
        "recherche": recherche,
        "type_actif": type_navire,
        "types": Escale.TYPE_CHOICES,
        "counts": counts,
        "updated_at": Escale.objects.aggregate(last=Max("updated_at"))["last"],
        "filtered": bool(recherche or type_navire),
    }

    if request.headers.get("HX-Request") == "true":
        return render(request, "navires/partials/escale_table.html", context)

    return render(request, "navires/escale_list.html", context)


def croisiere_list(request):
    """Calendrier des escales de croisière : à venir / passées, recherche, mise à jour HTMX."""
    from django.utils import timezone

    from apps.navires.models import Croisiere

    today = timezone.localdate()
    periode = request.GET.get("periode", "a_venir")
    periode = periode if periode in {"a_venir", "passees"} else "a_venir"
    recherche = request.GET.get("q", "").strip()[:80]

    base = Croisiere.objects.all()
    counts = {
        "a_venir": base.filter(date__gte=today).count(),
        "passees": base.filter(date__lt=today).count(),
    }
    queryset = base.filter(date__gte=today) if periode == "a_venir" else base.filter(date__lt=today)
    if recherche:
        queryset = queryset.filter(
            Q(navire__icontains=recherche) | Q(consignataire__icontains=recherche)
        )
    queryset = queryset.order_by("date" if periode == "a_venir" else "-date", "navire")

    context = {
        "bilan": BILAN_CROISIERE,
        "croisieres": queryset,
        "periode": periode,
        "recherche": recherche,
        "counts": counts,
        "prochaine": base.filter(date__gte=today).order_by("date", "navire").first(),
        "today": today,
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, "navires/partials/croisiere_table.html", context)
    return render(request, "navires/croisiere_list.html", context)
