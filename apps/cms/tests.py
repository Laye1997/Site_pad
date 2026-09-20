"""Tests de fumée — le socle répond."""

import pytest
from django.test import Client
from django.urls import reverse
from wagtail.models import Page, Site

from apps.cms.models import HomePage, StandardPage
from apps.media.models import MediaIndexPage


@pytest.mark.django_db
def test_healthz_repond_ok():
    response = Client().get("/healthz/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_homepage_exposes_seo_metadata():
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    homepage = HomePage(
        title="Port Autonome de Dakar",
        seo_title="Port Autonome de Dakar — Hub logistique maritime",
        search_description="Le hub logistique et maritime d'Afrique de l'Ouest.",
    )
    root.add_child(instance=homepage)
    homepage.save_revision().publish()

    response = Client().get(homepage.url)
    content = response.content.decode()

    assert response.status_code == 200
    expected_description = (
        '<meta name="description" content="Le hub logistique et maritime '
        'd&#x27;Afrique de l&#x27;Ouest.">'
    )
    assert expected_description in content
    expected_canonical = (
        f'<link rel="canonical" href="http://{response.wsgi_request.get_host()}'
        f'{response.wsgi_request.path}">'
    )
    assert expected_canonical in content
    assert '<meta property="og:type" content="website">' in content
    assert '<meta name="twitter:card" content="summary_large_image">' in content
    assert "/static/img/og-pad.jpg" in content


@pytest.mark.django_db
def test_navires_route_is_localized():
    assert reverse("navires:liste") == "/fr/navires/"


@pytest.mark.django_db
def test_classic_views_keep_wagtail_navigation_pages():
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    for title, slug in (
        ("Nous découvrir", "nous-decouvrir"),
        ("Infos pratiques", "infos-pratiques"),
        ("Opportunités d'affaires", "opportunites-affaires"),
    ):
        menu_page = StandardPage(title=title, slug=slug, show_in_menus=True)
        root.add_child(instance=menu_page)
        menu_page.save_revision().publish()
    media_page = MediaIndexPage(title="Espace média", slug="espace-media", show_in_menus=True)
    root.add_child(instance=media_page)
    media_page.save_revision().publish()
    marches = Client().get("/fr/marches/").content.decode()
    media = Client().get(media_page.url).content.decode()

    assert "Nous découvrir" in marches
    assert "Infos pratiques" in marches
    assert "Nous découvrir" in media
    assert "Opportunités d&#x27;affaires" in media


@pytest.mark.django_db
def test_homepage_uses_video_hero_without_duplicate_navires_ctas():
    root = Page.objects.get(depth=1)
    site, _ = Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    homepage = HomePage(title="Port Autonome de Dakar", intro="Un Port, Un But, Une Foi")
    root.add_child(instance=homepage)
    homepage.save_revision().publish()
    site.root_page = root
    site.save()

    response = Client().get(homepage.url)
    content = response.content.decode()

    assert '<video class="video-hero-media"' in content
    assert "/static/video/hero-pad.mp4" in content
    assert "Consulter les escales" not in content


@pytest.mark.django_db
def test_homepage_includes_padjoj2_without_replacing_primary_video():
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    homepage = HomePage(title="Port Autonome de Dakar")
    root.add_child(instance=homepage)
    homepage.save_revision().publish()

    content = Client().get(homepage.url).content.decode()

    assert "/static/video/hero-pad.mp4" in content
    assert "/static/video/joj-pad.mp4" in content
    assert "Le PAD au cœur des JOJ Dakar 2026" in content
