"""Template tags partagés par les pages éditoriales."""

from django import template
from django.http import Http404
from django.urls import Resolver404, reverse, translate_url
from django.utils import translation
from wagtail.models import Locale, Site

register = template.Library()


@register.filter
def get_item(value, key):
    """Retourne une valeur de dictionnaire ou une valeur vide."""
    if not value:
        return None
    return value.get(key)


@register.simple_tag(takes_context=True)
def slug_url(context, path):
    """URL d'une page Wagtail à partir de son chemin de slugs (ex. « nos-services/marchandises »).

    Évite les liens écrits en dur : suit la langue courante et retombe sur le chemin
    théorique si la page n'existe pas (aucune exception dans le gabarit).
    """
    components = path.strip("/").split("/")
    fallback = f"/{translation.get_language()}/{'/'.join(components)}/"
    request = context.get("request")
    site = Site.find_for_request(request) if request is not None else None
    if site is None:
        return fallback
    try:
        result = site.root_page.localized.route(request, components)
    except (Http404, Locale.DoesNotExist):
        return fallback
    return result.page.url or fallback


def _alternate_url(context, code):
    """URL de la page courante dans la langue `code` (traduction Wagtail sinon chemin traduit)."""
    request = context["request"]
    page = context.get("page")
    if page is not None and hasattr(page, "get_translations"):
        translated = page.get_translations().live().filter(locale__language_code=code).first()
        if translated is not None and translated.url:
            return translated.url
    try:
        alternate = translate_url(request.path, code)
    except Resolver404:
        alternate = ""
    return alternate if alternate and alternate != request.path else f"/{code}/"


@register.simple_tag(takes_context=True)
def language_url(context, code):
    """Lien du sélecteur de langue vers l'équivalent de la page courante."""
    if code == translation.get_language():
        return context["request"].path
    return _alternate_url(context, code)


@register.simple_tag(takes_context=True)
def absolute_language_url(context, code):
    """URL absolue d'une version linguistique, pour les balises hreflang."""
    request = context["request"]
    if code == translation.get_language():
        return request.build_absolute_uri(request.path)
    return request.build_absolute_uri(_alternate_url(context, code))


@register.simple_tag(takes_context=True)
def link_url(context, item):
    """URL d'un lien éditorial : page choisie, sinon `url:nom_de_route`, chemin absolu ou slugs."""
    page = item.get("page")
    if page is not None and page.url:
        return page.url
    path = (item.get("url_path") or "").strip()
    if path.startswith("url:"):
        return reverse(path[4:])
    if path.startswith(("/", "http")):
        return path
    return slug_url(context, path or "/")
