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
