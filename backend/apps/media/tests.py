import datetime as dt

import pytest
from django.test import Client
from django.utils import translation
from wagtail.models import Locale, Page, Site

from apps.media.models import ArticlePage, MediaIndexPage
from apps.media.services import latest_articles


@pytest.fixture
def media_index(db):
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    index = MediaIndexPage(
        title="Espace média",
        intro="Les actualités du Port Autonome de Dakar.",
        show_in_menus=True,
    )
    root.add_child(instance=index)
    index.save_revision().publish()
    for number in range(10):
        article = ArticlePage(
            title=f"Actualité portuaire {number + 1}",
            summary=f"Résumé de l'actualité {number + 1}.",
            category="actualite" if number % 2 == 0 else "communique",
            publication_date=dt.date(2026, 9, 19) - dt.timedelta(days=number),
        )
        index.add_child(instance=article)
        article.save_revision().publish()
    return index


@pytest.mark.django_db
def test_media_index_paginates_and_filters(media_index):
    response = Client().get(media_index.url)
    assert response.status_code == 200
    assert "Actualité portuaire 1" in response.content.decode()
    assert "Actualité portuaire 10" not in response.content.decode()
    assert response.context["articles"].paginator.num_pages == 2

    filtered = Client().get(f"{media_index.url}?categorie=communique")
    content = filtered.content.decode()
    assert filtered.context["active_category"] == "communique"
    assert "Actualité portuaire 2" in content
    assert "Actualité portuaire 1</a></h3>" not in content


@pytest.mark.django_db
def test_media_index_htmx_returns_article_grid(media_index):
    response = Client().get(media_index.url, HTTP_HX_REQUEST="true")
    content = response.content.decode()
    assert response.status_code == 200
    assert "Filtrer l'espace média" not in content
    assert "news-grid" in content


@pytest.mark.django_db
def test_update_notes_images_adds_photos_once(media_index):
    from django.core.management import call_command

    note = ArticlePage(
        title="Avis de signature : projet de terminal à conteneurs du Port de Ndayane",
        summary="Résumé",
        category="note",
        publication_date=dt.date(2026, 9, 1),
    )
    media_index.add_child(instance=note)
    note.save_revision().publish()

    call_command("update_notes_images")
    call_command("update_notes_images")
    note.refresh_from_db()

    assert note.cover_image_id is not None
    assert [b.block_type for b in note.body].count("image") == 3


@pytest.mark.django_db
def test_latest_articles_does_not_mix_locales(media_index):
    """Un article traduit en anglais ne doit pas doubler la liste affichée en français."""
    article = ArticlePage.objects.filter(locale=Locale.get_default()).first()
    en_locale, _ = Locale.objects.get_or_create(language_code="en")
    translated = article.copy_for_translation(en_locale, copy_parents=True)
    translated.save_revision().publish()

    translation.activate("fr")
    fr_titles = [a.title for a in latest_articles(limit=20)]
    translation.activate("en")
    en_titles = [a.title for a in latest_articles(limit=20)]

    assert fr_titles.count(article.title) == 1
    assert en_titles.count(article.title) == 1
