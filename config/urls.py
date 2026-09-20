"""Routage racine du projet."""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.core.views import healthz, robots_txt, search

# URLs non traduites (admin, API, santé, documents).
urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, name="sitemap"),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/", include("apps.api.urls")),
]

# URLs traduites (préfixe de langue /fr/ /en/) — pages Wagtail incluses.
urlpatterns += i18n_patterns(
    path("recherche/", search, name="recherche"),
    path("navires/", include("apps.navires.urls")),
    path("marches/", include("apps.marches.urls")),
    path("recrutement/", include("apps.recrutement.urls")),
    path("espace-pro/", include("apps.espace_pro.urls")),
    path("", include(wagtail_urls)),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
