"""Tests de l'accueil composé de sections modifiables."""

import datetime as dt

import pytest
from django.core.management import call_command
from django.test import Client, override_settings
from wagtail.models import Page, Site

from apps.cms.home_blocks import HomeSectionsBlock
from apps.cms.models import HomePage, StandardPage
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
    assert html.index('id="hm-news-title"') < html.index('id="hm-services-title"')
    assert "Mouvement des navires" in html
    assert "Heures de marées" in html
    for removed in ("hm-hub-title", "hm-pro-title", "hm-notices-title"):
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

    assert "hm-live" not in html
    assert "Attendus" not in html
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

    assert kinds[:6] == [
        "hero",
        "sponsoring",
        "president_vision",
        "director_word",
        "news",
        "service_band",
    ]
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


@pytest.mark.django_db
def test_update_home_services_puts_photo_on_first_tile_and_is_idempotent(home):
    call_command("seed_home_sections")
    call_command("update_home_services")
    call_command("update_home_services")

    html = _html(home)
    tiles = html.split('id="hm-services-title"')[1].split("</ul>")[0]

    assert "Accès nautique et balisage" in tiles
    assert "Accueil navires" not in tiles
    assert 'class="has-photo"' in tiles
    assert tiles.count('class="has-photo"') == 4
    assert "Trafic passagers" in tiles
    assert 'href="/fr/nos-services/acces-nautique-et-balisage/"' in tiles


@pytest.mark.django_db
def test_nautique_page_gets_both_photos_once_and_after_reseed(home):
    from apps.services.models import ServicePage

    call_command("seed_site_structure")
    call_command("update_service_nautique")
    call_command("update_service_nautique")
    call_command("seed_site_structure")

    page = ServicePage.objects.get(slug="acces-nautique-et-balisage")
    images = [b for b in page.body if b.block_type == "image"]
    html = Client().get(page.url).content.decode()

    assert len(images) == 2
    assert "Samba Laobé Fall" in html
    assert "bouée rouge" in html
    assert html.index("Samba Laobé Fall") < html.index("bouée rouge")


@pytest.mark.django_db
def test_trafic_passagers_section_has_subnav_tables_and_is_idempotent(home):
    call_command("seed_site_structure")
    call_command("seed_trafic_passagers")
    call_command("seed_trafic_passagers")
    from apps.services.models import ServicePage

    goree = ServicePage.objects.get(slug="dakar-goree")
    html = Client().get(goree.url).content.decode()
    index_html = Client().get(goree.get_parent().url).content.decode()

    assert 'class="service-subnav"' in html
    for title in ("Gare maritime", "Dakar-Ziguinchor", "Dakar-Gorée", "Politique Sûreté GMID"):
        assert title in html
    assert 'aria-current="page">Dakar-Gorée' in html
    assert '<th scope="col">Départ de Dakar</th>' in html
    assert "23h30 le vendredi" in html
    assert "1 500 F CFA" in html
    assert "800 801 802" in index_html
    assert html.count("<h1") == 1


@pytest.mark.django_db
def test_agrements_pages_offer_pdf_downloads_and_home_tile_points_to_them(home):
    call_command("seed_site_structure")
    call_command("seed_agrements")
    call_command("seed_agrements")
    call_command("seed_home_sections", "--force")

    page = StandardPage.objects.get(slug="obtenir-un-agrement")
    html = Client().get(page.url).content.decode()
    renew = Client().get(StandardPage.objects.get(slug="renouveler-son-agrement").url)
    forms = StandardPage.objects.get(slug="formulaires-declaration-chiffres-affaires")
    forms_html = Client().get(forms.url).content.decode()
    home_html = _html(home)

    assert "Profession de transitaire" in html
    assert html.count("/documents/") >= 7
    assert "Liste des pièces à fournir" in html
    assert "https://atlantis.portdakar.sn" in html
    assert renew.status_code == 200
    assert forms_html.count("/documents/") >= 5
    assert "/opportunites-affaires/procedures-agrements/obtenir-un-agrement/" in home_html


@pytest.mark.django_db
def test_marchandises_section_is_developed_with_subnav_and_storage_tables(home):
    from apps.services.models import ServicePage

    call_command("seed_site_structure")
    call_command("seed_marchandises")
    call_command("seed_marchandises")

    stock = ServicePage.objects.get(slug="stockage-entreposage")
    html = Client().get(stock.url).content.decode()
    manut = Client().get(ServicePage.objects.get(slug="manutention").url).content.decode()

    assert 'class="service-subnav"' in html
    for title in ("Manutention", "Stockage", "Enlèvement de marchandises"):
        assert title in html
    assert "98 351 m²" in html
    assert "20 jours" in html
    assert "Sea Invest" in manut
    assert "Manitowoc Grove GMK 5200" in manut


@pytest.mark.django_db
def test_update_home_services_adds_missing_section_after_news(home):
    _compose(
        home,
        ("hero", {"eyebrow": "", "title": "Titre", "intro": ""}),
        NEWS,
        ("join", {"title": "Rejoignez", "items": []}),
    )

    call_command("update_home_services")
    home.refresh_from_db()
    kinds = [block.block_type for block in home.sections]

    assert kinds == ["hero", "news", "service_band", "join"]
    assert "Mouvement des navires" in _html(home)


@pytest.mark.django_db
def test_every_internal_link_of_the_home_page_resolves(home):
    """Aucun lien interne de l'accueil ne doit mener à une 404 (structure complète en place)."""
    import re

    call_command("seed_site_structure")
    call_command("seed_home_sections", "--force")
    call_command("seed_trafic_passagers")
    call_command("seed_marchandises")
    call_command("seed_agrements")
    call_command("update_home_services")

    html = _html(home)
    links = set(re.findall(r'href="(/fr/[^"#?]*)', html))
    broken = [link for link in sorted(links) if Client().get(link, follow=True).status_code == 404]

    assert len(links) > 10
    assert broken == [], f"liens cassés sur l'accueil : {broken}"


@pytest.mark.django_db
def test_editors_get_the_wagtail_userbar_on_the_site_and_visitors_do_not(home, django_user_model):
    user = django_user_model.objects.create_superuser("editeur", "e@example.org", "x" * 20)

    anonymous = _html(home)
    client = Client()
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    editor = client.get(home.url).content.decode()

    assert "wagtail-userbar" not in anonymous
    assert "wagtail-userbar" in editor
    assert f"/admin/pages/{home.pk}/edit/" in editor


@pytest.mark.django_db
def test_fondation_page_and_section_menu_lists_only_its_own_pages(home):
    call_command("seed_site_structure")
    call_command("seed_fondation")
    call_command("seed_fondation")

    fondation = StandardPage.objects.get(slug="fondation")
    html = Client().get(fondation.url).content.decode()
    index = Client().get(fondation.get_parent().url).content.decode()

    assert "Historique de la Fondation" in html
    assert "SUCCESS" in html
    sidebar = html.split('class="section-sidebar"')[1].split("</aside>")[0]
    assert "Engagements" in sidebar
    assert "Fondation PAD" in sidebar
    assert "Nous découvrir" not in sidebar
    assert 'href="/fr/engagements/fondation/"' in index


@pytest.mark.django_db
def test_rubric_cards_on_home_show_photos_and_editor_choice_is_kept(home):
    Site.objects.filter(is_default_site=True).update(root_page=home)
    call_command("seed_site_structure")
    call_command("seed_home_sections", "--force")
    call_command("update_rubric_photos")
    call_command("update_rubric_photos")

    html = _html(home)
    grid = html.split('class="rubric-grid"')[1].split("</section>")[0]

    assert grid.count("rubric-card has-photo") == 7
    assert "Engagements" in grid
