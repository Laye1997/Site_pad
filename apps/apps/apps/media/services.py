"""Service applicatif de l'espace média (interface stable pour les autres apps)."""

from apps.media.models import ArticlePage


def latest_articles(limit: int = 3, category: str | None = None, exclude: list[str] | None = None):
    """Derniers articles publiés, du plus récent au plus ancien.

    `category` restreint à une catégorie ; `exclude` en écarte (ex. les notes aux usagers).
    """
    articles = ArticlePage.objects.live().public()
    if category:
        articles = articles.filter(category=category)
    if exclude:
        articles = articles.exclude(category__in=exclude)
    return list(articles.order_by("-publication_date", "-first_published_at")[:limit])


def user_notices(limit: int = 5):
    """Notes aux usagers (circulaires, avis) les plus récentes."""
    return latest_articles(limit, category="note")
