import datetime as dt

import pytest
from django.core.management import call_command
from django.test import Client

from apps.navires.models import Escale


@pytest.mark.django_db
def test_navires_default_lists_arrivees():
    Escale.objects.create(
        navire="MV Aster",
        type_navire="conteneur",
        pavillon="France",
        provenance="Le Havre",
        destination="Dakar",
        quai="Quai 2",
        date_arrivee=dt.date(2026, 9, 18),
        statut="attendu",
        consignataire="Dakar Port Services",
    )
    Escale.objects.create(
        navire="MV Borneo",
        type_navire="cargo",
        pavillon="Panama",
        provenance="Abidjan",
        destination="Nouadhibou",
        quai="Quai 5",
        date_arrivee=dt.date(2026, 9, 20),
        statut="parti",
        consignataire="Transit Sud",
    )

    response = Client().get("/fr/navires/")

    assert response.status_code == 200
    assert response.context["filtre_actif"] == "arrivees"
    assert "MV Aster" in response.content.decode()
    assert "MV Borneo" not in response.content.decode()


@pytest.mark.django_db
def test_navires_filters_by_category():
    Escale.objects.create(
        navire="MV Aster",
        type_navire="conteneur",
        pavillon="France",
        provenance="Le Havre",
        destination="Dakar",
        quai="Quai 2",
        date_arrivee=dt.date(2026, 9, 18),
        statut="a_quai",
        consignataire="Dakar Port Services",
    )
    Escale.objects.create(
        navire="MV Borneo",
        type_navire="cargo",
        pavillon="Panama",
        provenance="Abidjan",
        destination="Nouadhibou",
        quai="Quai 5",
        date_arrivee=dt.date(2026, 9, 20),
        statut="parti",
        consignataire="Transit Sud",
    )

    response = Client().get("/fr/navires/?filtre=departs")

    assert response.status_code == 200
    assert response.context["filtre_actif"] == "departs"
    assert "MV Borneo" in response.content.decode()
    assert "MV Aster" not in response.content.decode()


@pytest.mark.django_db
def test_navires_htmx_request_returns_partial_table():
    Escale.objects.create(
        navire="MV Aster",
        type_navire="conteneur",
        pavillon="France",
        provenance="Le Havre",
        destination="Dakar",
        quai="Quai 2",
        date_arrivee=dt.date(2026, 9, 18),
        statut="attendu",
        consignataire="Dakar Port Services",
    )

    response = Client().get("/fr/navires/?filtre=arrivees", HTTP_HX_REQUEST="true")

    assert response.status_code == 200
    assert 'aria-live="polite"' in response.content.decode()
    assert "MV Aster" in response.content.decode()


@pytest.mark.django_db
def test_seed_navires_covers_all_statuses():
    call_command("seed_navires", verbosity=0)

    assert set(Escale.objects.values_list("statut", flat=True)) == {
        "attendu",
        "a_quai",
        "parti",
    }


def _escales():
    Escale.objects.create(
        navire="MV Aster",
        type_navire="conteneur",
        pavillon="France",
        provenance="Le Havre",
        destination="Dakar",
        date_arrivee=dt.date(2026, 9, 18),
        statut="attendu",
        consignataire="Dakar Port Services",
    )
    Escale.objects.create(
        navire="MS Céleste",
        type_navire="passagers",
        pavillon="Espagne",
        provenance="Casablanca",
        destination="Dakar",
        date_arrivee=dt.date(2026, 9, 20),
        statut="a_quai",
    )
    Escale.objects.create(
        navire="MV Borneo",
        type_navire="cargo",
        pavillon="Panama",
        provenance="Abidjan",
        destination="Nouadhibou",
        date_arrivee=dt.date(2026, 9, 19),
        statut="parti",
    )


@pytest.mark.django_db
def test_navires_search_matches_ship_port_and_consignee():
    _escales()

    by_ship = Client().get("/fr/navires/?q=aster").content.decode()
    by_port = Client().get("/fr/navires/?q=casablanca").content.decode()
    by_consignee = Client().get("/fr/navires/?q=port+services").content.decode()

    assert "MV Aster" in by_ship and "MS Céleste" not in by_ship
    assert "MS Céleste" in by_port and "MV Aster" not in by_port
    assert "MV Aster" in by_consignee


@pytest.mark.django_db
def test_navires_type_filter_and_invalid_values_are_ignored():
    _escales()

    passagers = Client().get("/fr/navires/?type=passagers").content.decode()
    invalid = Client().get("/fr/navires/?type=<script>&filtre=nimporte").content.decode()

    assert "MS Céleste" in passagers and "MV Aster" not in passagers
    assert "MV Aster" in invalid and "MS Céleste" in invalid
    assert "<script>alert" not in invalid


@pytest.mark.django_db
def test_navires_tabs_show_counts_and_htmx_partial_has_no_layout():
    _escales()

    full = Client().get("/fr/navires/")
    partial = Client().get("/fr/navires/?filtre=departs", HTTP_HX_REQUEST="true")

    assert full.context["filtres"]["arrivees"]["count"] == 2
    assert full.context["filtres"]["a_quai"]["count"] == 1
    assert full.context["filtres"]["departs"]["count"] == 1
    assert "fleet-kpis" in full.content.decode()
    content = partial.content.decode()
    assert "MV Borneo" in content
    assert "<html" not in content
    assert "1 escale" in content


@pytest.mark.django_db
def test_seed_croisieres_is_idempotent_and_page_splits_upcoming_and_past():
    from django.core.management import call_command

    from apps.navires.models import Croisiere

    call_command("seed_croisieres")
    call_command("seed_croisieres")

    assert Croisiere.objects.count() == 37
    upcoming = Client().get("/fr/navires/croisieres/").content.decode()
    past = Client().get("/fr/navires/croisieres/?periode=passees").content.decode()
    searched = Client().get("/fr/navires/croisieres/?periode=passees&q=bellot").content.decode()

    assert "QUEEN VICTORIA" in upcoming and "SEVEN SEAS SPLENDOR" not in upcoming
    assert "SEVEN SEAS SPLENDOR" in past and "QUEEN VICTORIA" not in past
    assert "LE BELLOT" in searched and "SEVEN SEAS" not in searched
    assert "Prochaine escale" in upcoming


@pytest.mark.django_db
def test_croisiere_htmx_partial_has_no_layout():
    from apps.navires.models import Croisiere

    Croisiere.objects.create(date=dt.date(2099, 1, 1), navire="TEST SHIP", poste="15")
    response = Client().get("/fr/navires/croisieres/", HTTP_HX_REQUEST="true")

    assert "TEST SHIP" in response.content.decode()
    assert "<html" not in response.content.decode()


@pytest.mark.django_db
def test_croisieres_page_shows_banner_and_official_bilan():
    html = Client().get("/fr/navires/croisieres/").content.decode()

    assert "mouvement-croisiere.jpg" in html
    assert "Bilan croisière" in html
    assert "+12 771" in html and "+17 850" in html and "+15 554" in html
