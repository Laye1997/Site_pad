"""Points d'entrée de l'API publique (lecture seule, contrat stable v1)."""

from django.urls import path

from apps.api import views
from apps.core.views import healthz

app_name = "api"

urlpatterns = [
    path("health/", healthz, name="health"),
    path("v1/escales/", views.EscaleListView.as_view(), name="escales"),
    path("v1/certifications/", views.CertificationListView.as_view(), name="certifications"),
]
