from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET


def healthz(request):
    """Sonde de santé pour le monitoring et l'orchestrateur."""
    return JsonResponse({"status": "ok"})


@require_GET
def robots_txt(request):
    """Consignes d'indexation : l'administration et l'API technique ne sont pas indexées."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /django-admin/",
        "Disallow: /api/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def search(request):
    """Recherche plein texte dans les pages publiées (moteur Wagtail, résultats paginés)."""
    from django.core.paginator import Paginator
    from django.shortcuts import render
    from wagtail.models import Page

    query = request.GET.get("q", "").strip()[:100]
    results = Page.objects.none()
    if query:
        results = Page.objects.live().public().search(query)
    page = Paginator(results, 10).get_page(request.GET.get("page"))
    return render(request, "search.html", {"query": query, "results": page})
