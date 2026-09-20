"""Vues publiques des marchés publics."""

from django.shortcuts import render

from apps.marches.models import AppelOffre

FILTERS = {
    "tous": {"label": "Tous", "field": None},
    "ouverts": {"label": "Ouverts", "field": {"statut": "ouvert"}},
    "clotures": {"label": "Clôturés", "field": {"statut": "cloture"}},
    "attribues": {"label": "Attribués", "field": {"statut": "attribue"}},
}


def marche_list(request):
    """Affiche les marchés avec filtres GET et réponse partielle HTMX."""
    filtre = request.GET.get("filtre", "tous")
    filtre_actif = filtre if filtre in FILTERS else "tous"
    queryset = AppelOffre.objects.all()
    filters = FILTERS[filtre_actif]["field"]
    if filters:
        queryset = queryset.filter(**filters)

    context = {
        "marches": queryset,
        "filtre_actif": filtre_actif,
        "filtres": FILTERS,
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, "marches/partials/marche_table.html", context)
    return render(request, "marches/marche_list.html", context)
