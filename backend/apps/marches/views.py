"""Vues publiques des marchés publics."""

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.core.models import ListHeaderSettings
from apps.marches.models import AppelOffre

FILTERS = {
    "tous": {"label": _("Tous"), "field": None},
    "ouverts": {"label": _("Ouverts"), "field": {"statut": "ouvert"}},
    "clotures": {"label": _("Clôturés"), "field": {"statut": "cloture"}},
    "attribues": {"label": _("Attribués"), "field": {"statut": "attribue"}},
}


def marche_list(request):
    """Affiche les marchés avec filtres GET et réponse partielle HTMX."""
    filtre = request.GET.get("filtre", "tous")
    filtre_actif = filtre if filtre in FILTERS else "tous"
    queryset = AppelOffre.objects.all()
    filters = FILTERS[filtre_actif]["field"]
    if filters:
        queryset = queryset.filter(**filters)

    texts = ListHeaderSettings.for_request(request)
    context = {
        "eyebrow": texts.display("marches_eyebrow"),
        "page_title": texts.display("marches_title"),
        "intro": texts.display("marches_intro"),
        "marches": queryset,
        "filtre_actif": filtre_actif,
        "filtres": FILTERS,
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, "marches/partials/marche_table.html", context)
    return render(request, "marches/marche_list.html", context)
