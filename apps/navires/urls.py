"""Routes publiques du module navires."""

from django.urls import path

from apps.navires.views import croisiere_list, escale_list

app_name = "navires"

urlpatterns = [
    path("", escale_list, name="liste"),
    path("croisieres/", croisiere_list, name="croisieres"),
]
