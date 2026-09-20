"""Point d'entrée explicite conservé pour l'app média."""

from django.urls import path

from apps.media.views import media_index_view

app_name = "media"

urlpatterns = [path("", media_index_view, name="index")]
