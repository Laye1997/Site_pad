"""Contexte public de l'espace média."""

from django.core.paginator import Paginator
from django.shortcuts import render

from apps.media.models import ArticlePage

CATEGORIES = {
    "tous": "Tous",
    "actualite": "Actualités",
    "communique": "Communiqués",
    "evenement": "Événements",
    "photos": "Photos et vidéos",
}


def media_index(request, page):
    """Ajoute les articles filtrés et paginés au contexte de l'index."""
    category = request.GET.get("categorie", "tous")
    active_category = category if category in CATEGORIES else "tous"
    articles = ArticlePage.objects.live().public().child_of(page).specific()
    if active_category != "tous":
        articles = articles.filter(category=active_category)

    paginator = Paginator(articles.order_by("-publication_date", "-first_published_at"), 9)
    context = page.get_context(request)
    context["articles"] = paginator.get_page(request.GET.get("page"))
    context["categories"] = CATEGORIES
    context["active_category"] = active_category
    return context


def media_index_view(request, page):
    """Rend l'index média complet ou son fragment HTMX."""
    context = media_index(request, page)
    template = (
        "media/partials/article_grid.html"
        if request.headers.get("HX-Request")
        else "media/media_index_page.html"
    )
    return render(request, template, context)
