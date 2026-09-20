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


@pytest.mark.django_db
def test_default_layout_has_single_h1_and_news_right_after_sponsoring(home):
    html = _html(home)

    assert html.count("<h1") == 1
    assert html.index('id="joj-title"') < html.index('id="hm-news-title"')
    assert html.index('id="hm-news-title"') < html.index('id="hm-services-title"')


@pytest.mark.django_db
def test_editor_composition_replaces_default_sections(home):
    home.sections = HomeSectionsBlock().to_python(
        [
            {"type": "hero", "value": {"eyebrow": "", "title": "Titre éditeur", "intro": ""}},
            {
                "type": "news",
                "value": {"title": "Fil infos", "count": 2, "all_link_label": "Tout"},
            },
        ]
    )
    home.save_revision().publish()

    html = _html(home)

    assert "Titre éditeur" in html
    assert "Fil infos" in html
    assert 'id="joj-title"' not in html
    assert 'id="hm-services-title"' not in html


@pytest.mark.django_db
def test_news_and_notices_are_split_by_category(home):
    index = MediaIndexPage(title="Espace média", slug="espace-media")
    home.add_child(instance=index)
    _article(index, "Nouveau quai inauguré", "actualite", 3)
    _article(index, "Circulaire fret", "note", 4)

    html = _html(home)
    news_part = html.split('id="hm-news-title"')[1].split("</section>")[0]
    notices_part = html.split('id="hm-notices-title"')[1].split("</section>")[0]

    assert "Nouveau quai inauguré" in news_part
    assert "Circulaire fret" not in news_part
    assert "Circulaire fret" in notices_part
    assert "Nouveau quai inauguré" not in notices_part


@pytest.mark.django_db
def test_sections_show_live_ships_tender_and_valid_certifications(home):
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

    assert "MV Aster" in html
    assert "Acquisition de deux ascenseurs" in html
    assert "ISO 9001" in html
    assert "ISO 14001" not in html


@pytest.mark.django_db
def test_ship_movement_can_be_hidden_by_feature_flag(home):
    flags = {"consent_banner": True, "public_api": True, "home_ship_movement": False}
    with override_settings(FEATURES=flags):
        html = _html(home)

    assert "Mouvement des navires" not in html
    assert 'id="hm-services-title"' in html


@pytest.mark.django_db
def test_service_links_resolve_django_routes_and_missing_pages(home):
    html = _html(home)

    assert 'href="/fr/recrutement/postuler/"' in html
    assert 'href="/fr/nos-services/marchandises/"' in html


@pytest.mark.django_db
def test_seed_home_sections_makes_default_layout_editable_and_is_idempotent(home):
    call_command("seed_home_sections")
    home.refresh_from_db()
    kinds = [block.block_type for block in home.sections]

    assert kinds[:5] == ["hero", "sponsoring", "president_vision", "director_word", "news"]
    home.sections = HomeSectionsBlock().to_python(
        [{"type": "hero", "value": {"eyebrow": "", "title": "Perso", "intro": ""}}]
    )
    home.save_revision().publish()
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
