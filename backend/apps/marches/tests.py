import datetime as dt

import pytest
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from apps.marches.models import AppelOffre


@pytest.fixture
def marches(db):
    AppelOffre.objects.create(
        reference="PAD-AO-2026-001",
        objet="Maintenance du terminal à conteneurs",
        type_marche="appel_offres",
        date_publication=dt.date(2026, 9, 5),
        date_limite=dt.date(2026, 10, 5),
        statut="ouvert",
    )
    AppelOffre.objects.create(
        reference="PAD-AT-2026-004",
        objet="Matériels de sécurité portuaire",
        type_marche="avis_attribution",
        date_publication=dt.date(2026, 8, 22),
        statut="attribue",
    )


@pytest.mark.django_db
def test_marches_list_and_status_filter(marches):
    response = Client().get("/fr/marches/")
    assert response.status_code == 200
    assert "PAD-AO-2026-001" in response.content.decode()
    assert "PAD-AT-2026-004" in response.content.decode()

    filtered = Client().get("/fr/marches/?filtre=ouverts")
    content = filtered.content.decode()
    assert filtered.context["filtre_actif"] == "ouverts"
    assert "PAD-AO-2026-001" in content
    assert "PAD-AT-2026-004" not in content


@pytest.mark.django_db
def test_marches_htmx_returns_only_table(marches):
    response = Client().get("/fr/marches/?filtre=attribues", HTTP_HX_REQUEST="true")
    content = response.content.decode()
    assert response.status_code == 200
    assert "PAD-AT-2026-004" in content
    assert "Filtrer les publications" not in content
    assert "<table>" in content


@pytest.mark.django_db
def test_seed_marches_creates_publication_types():
    call_command("seed_marches", verbosity=0)
    assert set(AppelOffre.objects.values_list("type_marche", flat=True)) == {
        "appel_offres",
        "avis_attribution",
        "plan_passation",
    }


def test_marches_url_is_localized():
    assert reverse("marches:liste") == "/fr/marches/"
