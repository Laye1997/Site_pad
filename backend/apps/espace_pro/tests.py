"""L'Espace Pro est une page CMS (voir apps.cms.management.commands.seed_espace_pro),
pas un compte local : ces tests vérifient la passerelle vers le portail Atlantis."""

import pytest
from django.core.management import call_command
from django.test import Client


@pytest.mark.django_db
def test_espace_pro_page_links_to_atlantis_portal():
    call_command("seed_site_structure")
    call_command("seed_espace_pro")

    response = Client().get("/fr/espace-pro/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "atlantis.portdakar.sn" in content
    assert "Procédures et agréments" in content or "procedures-agrements" in content


@pytest.mark.django_db
def test_old_login_url_no_longer_served():
    response = Client().get("/fr/espace-pro/connexion/")

    assert response.status_code == 404
