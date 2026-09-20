"""Routes de l'espace professionnel."""

from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.espace_pro.views import ProLoginView, dashboard

app_name = "espace_pro"

urlpatterns = [
    path("connexion/", ProLoginView.as_view(), name="login"),
    path("deconnexion/", LogoutView.as_view(), name="logout"),
    path("", dashboard, name="dashboard"),
]
