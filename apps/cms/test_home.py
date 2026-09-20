"""Tests de l'accueil composé de sections modifiables."""

import datetime as dt

import pytest
from django.core.management import call_command
from django.test import Client, override_settings
from wagtail.models import Page, Site

from apps.cms.home_blocks import HomeSectionsBlock
from apps.cms.models import HomePage
from apps.marches.models import AppelOffre
from apps.media.models import ArticlePage, MediaIndexPage
from apps.navires.models import Escale
from apps.qualite.models import Certification


@pytest.fixture
def home(db):
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost", defaults={"root_page": root, "is_default_site": True}
    )
    page = HomePage(title="Accueil")
    root.add_child(instance=page)
    page.save_revision().publish()
    return page


def _html(page):
    return Client().get(page.url).content.decode()


def _article(index, title, category="actualite", day=1):
    article = ArticlePage(
        title=title,
        summary=f"Résumé {title}",
        category=category,
        publication_date=dt.date(2026, 9, day),
    )
    index.add_child(instance=article)
    article.save_revision().publish()
    return article


def _compose(page, *sections):
    """Enregistre une composition explicite (comme le ferait un rédacteur dans l'éditeur)."""
    page.sections = HomeSectionsBlock().to_python(
        [{"type": kind, "value": value} for kind, value in sections]
    )
    page.save_revision().publish()


NEWS = ("news", {"title": "Actualités", "count": 4, "all_link_label": "Tout"})
SERVICES = (
    "service_band",
    {
        "services_title": "Offre de service",
        "services": [
            {
                "label": "Marchandises",
                "icon": "doc",
                "page": None,
                "url_path": "nos-services/marchandises",
            }
        ],
        "show_movement": True,
        "movement_title": "Mouvement des navires",
    },
)


@pytest.mark.django_db
def test_default_layout_order_and_removed_sections(home):
    html = _html(home)

    assert html.count("<h1") == 1
    assert html.index('id="joj-title"') < html.index('id="hm-pres-title"')
    assert html.index('id="hm-pres-title"') < html.index('id="hm-dg-title"')
    assert html.index('id="hm-dg-title"') < html.index('id="hm-news-title"')
    for removed in ("hm-services-title", "hm-hub-title", "hm-pro-title", "hm-notices-title"):
        assert f'id="{removed}"' not in html
    assert "Faire des affaires au port" not in html
    assert "Rejoignez le port" not in html


@pytest.mark.django_db
def test_editor_composition_replaces_default_sections(home):
    _compose(
        home,
        ("hero", {"eyebrow": "", "title": "Titre éditeur", "intro": ""}),
        ("news", {"title": "Fil infos", "count": 2, "all_link_label": "Tout"}),
    )

    html = _html(home)

    assert "Titre éditeur" in html
    assert "Fil infos" in html
    assert 'id="joj-title"' not in html


@pytest.mark.django_db
def test_news_and_notices_are_split_by_category(home):
    index = MediaIndexPage(title="Espace média", slug="espace-media")
    home.add_child(instance=index)
    _article(index, "Nouveau quai inauguré", "actualite", 3)
    _article(index, "Circulaire fret", "note", 4)
    notices = {
        "figures_title": "Trafic",
        "figures_image": None,
        "figures_alt": "",
        "title": "Note aux usagers",
        "count": 5,
    }
    _compose(home, NEWS, ("notices", notices))

    html = _html(home)
    news_part = html.split('id="hm-news-title"')[1].split("</section>")[0]
    notices_part = html.split('id="hm-notices-title"')[1].split("</section>")[0]

    assert "Nouveau quai inauguré" in news_part
    assert "Circulaire fret" not in news_part
    assert "Circulaire fret" in notices_part
    assert "Nouveau quai inauguré" not in notices_part


@pytest.mark.django_db
def test_optional_sections_show_live_ships_and_tender(home):
    Escale.objects.create(
        navire="MV Aster",
        pavillon="Sénégal",
        provenance="Abidjan",
        destination="Dakar",
        date_arrivee=dt.date(2026, 9, 20),
        statut="attendu",
    )
    AppelOffre.objects.create(
        objet="Acquisition de deux ascenseurs",
        reference="AO-1",
        date_publication=dt.date(2026, 9, 1),
        date_limite=dt.date.today() + dt.timedelta(days=10),
    )
    business = {"title": "Affaires", "side_title": "News", "side_text": "Avis"}
    _compose(home, SERVICES, ("business", business))

    html = _html(home)

    assert "MV Aster" in html
    assert "Acquisition de deux ascenseurs" in html
    assert 'href="/fr/nos-services/marchandises/"' in html


@pytest.mark.django_db
def test_default_page_shows_only_valid_certifications(home):
    today = dt.date.today()
    for referentiel, days in (("iso9001", 60), ("iso14001", -3)):
        Certification.objects.create(
            referentiel=referentiel,
            perimetre="Port",
            organisme="Org",
            date_emission=today - dt.timedelta(days=200),
            date_validite=today + dt.timedelta(days=days),
        )

    html = _html(home)

    assert "ISO 9001" in html
    assert "ISO 14001" not in html


@pytest.mark.django_db
def test_ship_movement_can_be_hidden_by_feature_flag(home):
    _compose(home, SERVICES)
    flags = {"consent_banner": True, "public_api": True, "home_ship_movement": False}
    with override_settings(FEATURES=flags):
        html = _html(home)

    assert "Mouvement des navires" not in html
    assert 'id="hm-services-title"' in html


@pytest.mark.django_db
def test_seed_home_sections_makes_default_layout_editable_and_is_idempotent(home):
    call_command("seed_home_sections")
    home.refresh_from_db()
    kinds = [block.block_type for block in home.sections]

    assert kinds[:5] == ["hero", "sponsoring", "president_vision", "director_word", "news"]
    assert "service_band" not in kinds
    _compose(home, ("hero", {"eyebrow": "", "title": "Perso", "intro": ""}))
    call_command("seed_home_sections")
    home.refresh_from_db()

    assert [block.block_type for block in home.sections] == ["hero"]


@pytest.mark.django_db
def test_director_word_comes_right_after_sponsoring_and_before_news(home):
    html = _html(home)

    assert "Un Port Autonome de Dakar Bou Bess" in html
    assert "sept priorités" in html
    assert html.index('id="joj-title"') < html.index('id="hm-dg-title"')
    assert html.index('id="hm-dg-title"') < html.index('id="hm-news-title"')
    assert "/static/img/mot-dg.jpg" in html


@pytest.mark.django_db
def test_president_vision_comes_before_director_word(home):
    html = _html(home)

    assert "Bassirou Diomaye Faye" in html
    assert "Môle 4" in html
    assert html.count('class="hm-pillar"') == 3
    assert html.index('id="joj-title"') < html.index('id="hm-pres-title"')
    assert html.index('id="hm-pres-title"') < html.index('id="hm-dg-title"')
    assert "/static/img/president.jpg" in html


@pytest.mark.django_db
def test_setup_site_moves_pages_under_home_and_removes_default_welcome_page():
    from apps.cms.models import StandardPage

    root = Page.objects.get(depth=1)
    welcome = Page.objects.get(depth=2)
    section = StandardPage(title="Nous découvrir", slug="nous-decouvrir")
    welcome.add_child(instance=section)
    section.save_revision().publish()

    call_command("setup_site", "--host", "10.0.0.1", "--port", "1515")
    call_command("setup_site", "--host", "10.0.0.1", "--port", "1515")

    home = HomePage.objects.get()
    site = Site.objects.get(is_default_site=True)
    assert site.root_page_id == home.pk
    assert (site.hostname, site.port) == ("10.0.0.1", 1515)
    assert not Page.objects.filter(pk=welcome.pk).exists()
    assert home.get_children().filter(slug="nous-decouvrir").exists()
    assert Page.objects.filter(depth=2).count() == 1
    assert root.pk
