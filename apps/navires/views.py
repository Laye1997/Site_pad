"""Vues publiques du mouvement des navires."""

from django.db.models import Q
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


def escale_list(request):
    """Affiche la liste des escales, filtrable et compatible HTMX."""
    filtre = request.GET.get("filtre", "arrivees")
    filtre_actif = filtre if filtre in FILTRES else "arrivees"
    queryset = Escale.objects.filter(FILTRES[filtre_actif]["query"]).order_by(
        "date_arrivee",
        "navire",
    )

    context = {
        "escales": queryset,
        "filtre_actif": filtre_actif,
        "filtres": FILTRES,
    }

    if request.headers.get("HX-Request") == "true":
        return render(request, "navires/partials/escale_table.html", context)

    return render(request, "navires/escale_list.html", context)
