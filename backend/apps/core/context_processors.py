"""Contexte partagé par les pages Wagtail et les vues Django classiques."""

from django.conf import settings
from wagtail.models import Site

# Pages légales et transverses affichées dans le pied de page si elles sont publiées.
FOOTER_PAGE_SLUGS = (
    "mentions-legales",
    "confidentialite",
    "accessibilite",
    "plan-du-site",
)


def site_navigation(request):
    """Expose les pages principales et les pages légales dans toutes les vues du site."""
    site = Site.find_for_request(request) or Site.objects.filter(is_default_site=True).first()
    if not site:
        return {"menu_pages": [], "footer_pages": []}
    children = site.root_page.get_children().live()
    footer_pages = sorted(
        children.filter(slug__in=FOOTER_PAGE_SLUGS),
        key=lambda page: FOOTER_PAGE_SLUGS.index(page.slug),
    )
    return {
        "menu_pages": children.in_menu().specific(),
        "footer_pages": footer_pages,
    }


def features(request):
    """Expose les feature flags (activer/désactiver une fonction par variable d'environnement)."""
    return {
        "FEATURES": settings.FEATURES,
        "SOCIAL_LINKS": {k: v for k, v in settings.SOCIAL_LINKS.items() if v},
    }
