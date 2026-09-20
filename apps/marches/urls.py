"""Routes publiques des marchés publics."""

from django.urls import path

from apps.marches.views import marche_list

app_name = "marches"

urlpatterns = [
    path("", marche_list, name="liste"),
]
