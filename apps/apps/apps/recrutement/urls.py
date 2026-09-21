"""Routes du formulaire de recrutement."""

from django.urls import path

from apps.recrutement.views import apply, confirmation

app_name = "recrutement"

urlpatterns = [
    path("postuler/", apply, name="apply"),
    path("confirmation/", confirmation, name="confirmation"),
]
