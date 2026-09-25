"""Tests du socle : SEO technique, API publique, sécurité, alertes, redirections, pages légales."""

import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from django.core import mail
from django.core.management import call_command
from django.test import Client, override_settings
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Page, Site

from apps.cms.models import HomePage, StandardPage
from apps.navires.models import Escale
from apps.qualite.models import Certification
from apps.qualite.tasks import alert_expiring_certifications

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def site_root():
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost", defaults={"root_page": root, "is_default_site": True}
    )
    return root


def _certification(referentiel, days_left):
    today = date.today()
    return Certification.objects.create(
        referentiel=referentiel,
        perimetre="Port de Dakar",
        organisme="Organisme",
        date_emission=today - timedelta(days=300),
        date_validite=today + timedelta(days=days_left),
    )


@pytest.mark.django_db
def test_robots_txt_hides_admin_and_points_to_sitemap():
    response = Client().get("/robots.txt")
    body = response.content.decode()

    assert response["Content-Type"].startswith("text/plain")
    assert "Disallow: /admin/" in body
    assert "Sitemap: http://testserver/sitemap.xml" in body


@pytest.mark.django_db
def test_sitemap_lists_published_pages(site_root):
    page = StandardPage(title="Nous découvrir", slug="nous-decouvrir")
    site_root.add_child(instance=page)
    page.save_revision().publish()

    response = Client().get("/sitemap.xml")

    assert response.status_code == 200
    assert "nous-decouvrir" in response.content.decode()


@pytest.mark.django_db
def test_public_api_lists_ships_and_only_valid_certifications():
    Escale.objects.create(
        navire="MV Aster",
        pavillon="Sénégal",
        provenance="Abidjan",
        destination="Dakar",
        date_arrivee=date(2026, 9, 20),
        statut="a_quai",
    )
    _certification("iso9001", 100)
    _certification("iso14001", -5)

    escales = Client().get("/api/v1/escales/?statut=a_quai").json()["results"]
    certifications = Client().get("/api/v1/certifications/").json()["results"]

    assert [e["navire"] for e in escales] == ["MV Aster"]
    assert [c["referentiel"] for c in certifications] == ["iso9001"]
    assert Client().get("/api/v1/escales/?statut=parti").json()["results"] == []


@pytest.mark.django_db
def test_public_api_can_be_switched_off_by_feature_flag():
    with override_settings(FEATURES={"public_api": False, "consent_banner": True}):
        assert Client().get("/api/v1/escales/", follow=True).status_code == 404


@pytest.mark.django_db
def test_pages_ship_no_inline_script_so_csp_can_forbid_it(site_root):
    homepage = HomePage(title="Port Autonome de Dakar")
    site_root.add_child(instance=homepage)
    homepage.save_revision().publish()

    for url in (homepage.url, "/fr/marches/", "/fr/navires/"):
        html = Client().get(url).content.decode()
        inline = [
            tag
            for tag in re.findall(r"<script\b[^>]*>", html)
            if "src=" not in tag and "application/ld+json" not in tag
        ]
        assert inline == [], f"script inline sur {url}"
        assert " style=" not in html, f"style inline sur {url}"


@pytest.mark.django_db
def test_main_menu_is_visible_without_javascript():
    html = Client().get("/fr/marches/").content.decode()

    assert '<nav id="primary-nav" class="main-nav"' in html
    assert re.search(r'<nav id="primary-nav"[^>]*\shidden', html) is None


@pytest.mark.django_db
def test_language_switcher_and_hreflang_point_to_equivalent_page():
    html = Client().get("/fr/marches/").content.decode()

    assert 'hreflang="en" href="http://testserver/en/marches/"' in html
    assert 'href="/en/marches/" lang="en"' in html


@pytest.mark.django_db
def test_english_interface_is_translated():
    html = Client().get("/en/marches/").content.decode()

    assert "Skip to main content" in html
    assert "Aller au contenu principal" not in html


@pytest.mark.django_db
def test_footer_shows_only_published_legal_pages(site_root):
    call_command("seed_legal_pages")
    assert "Mentions légales" not in Client().get("/fr/marches/").content.decode()

    page = StandardPage.objects.get(slug="mentions-legales")
    page.save_revision().publish()

    assert "Mentions légales" in Client().get("/fr/marches/").content.decode()


@pytest.mark.django_db
def test_seed_legal_pages_creates_drafts_without_overwriting(site_root):
    call_command("seed_legal_pages")
    call_command("seed_legal_pages")

    pages = StandardPage.objects.filter(slug__in=["mentions-legales", "confidentialite"])
    assert pages.count() == 2
    assert not any(page.live for page in pages)


@pytest.mark.django_db
def test_consent_banner_can_be_disabled_by_feature_flag():
    assert 'id="consent-banner"' in Client().get("/fr/marches/").content.decode()
    with override_settings(FEATURES={"public_api": True, "consent_banner": False}):
        assert 'id="consent-banner"' not in Client().get("/fr/marches/").content.decode()


@pytest.mark.django_db
def test_certification_alert_emails_admins_only_for_expiring_certificates(
    settings, django_user_model
):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    django_user_model.objects.create_superuser("admin", "admin@example.org", "x" * 20)
    _certification("iso9001", 30)
    _certification("iso14001", 400)

    count = alert_expiring_certifications()

    assert count == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["admin@example.org"]
    assert "ISO 9001" in mail.outbox[0].body
    assert "ISO 14001" not in mail.outbox[0].body


@pytest.mark.django_db
def test_import_redirects_creates_permanent_redirect_to_page(site_root, tmp_path):
    parent = StandardPage(title="Nous découvrir", slug="nous-decouvrir")
    site_root.add_child(instance=parent)
    parent.save_revision().publish()
    csv_file = tmp_path / "redirects.csv"
    csv_file.write_text(
        "ancienne_url,nouvelle_page\n/fr/node/12,nous-decouvrir\n/fr/node/13,inconnue\n",
        encoding="utf-8",
    )

    call_command("import_drupal_redirects", str(csv_file))
    call_command("import_drupal_redirects", str(csv_file))

    redirect = Redirect.objects.get(old_path="/fr/node/12")
    assert redirect.is_permanent
    assert redirect.redirect_page_id == parent.id
    assert Redirect.objects.count() == 1


def _prod_import(secret):
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings.prod"}
    env.pop("DJANGO_SECRET_KEY", None)
    if secret is not None:
        env["DJANGO_SECRET_KEY"] = secret
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", "import config.settings.prod"],
        cwd=BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_refuses_default_or_short_secret_key():
    assert _prod_import(None).returncode != 0
    assert _prod_import("change-me-in-prod").returncode != 0
    assert _prod_import("x" * 40).returncode == 0


@pytest.mark.django_db
def test_media_is_served_by_django_only_when_serve_media_is_enabled(tmp_path, settings):
    """Sans nginx (hébergeur), SERVE_MEDIA=true rend les photos téléversées accessibles."""
    import importlib

    from django.test import Client
    from django.urls import clear_url_caches

    import config.urls

    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "photo.txt").write_text("contenu", encoding="utf-8")
    settings.MEDIA_ROOT = tmp_path
    try:
        settings.SERVE_MEDIA = False
        importlib.reload(config.urls)
        clear_url_caches()
        assert Client().get("/media/images/photo.txt").status_code == 404

        settings.SERVE_MEDIA = True
        importlib.reload(config.urls)
        clear_url_caches()
        response = Client().get("/media/images/photo.txt")
        assert response.status_code == 200
        assert b"".join(response.streaming_content) == b"contenu"
        assert Client().get("/media/../manage.py").status_code in (400, 404)
    finally:
        settings.SERVE_MEDIA = False
        importlib.reload(config.urls)
        clear_url_caches()
