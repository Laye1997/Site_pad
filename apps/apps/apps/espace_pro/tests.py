import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.mark.django_db
def test_professional_dashboard_requires_login():
    response = Client().get("/fr/espace-pro/")

    assert response.status_code == 302
    assert "/fr/espace-pro/connexion/" in response.url


@pytest.mark.django_db
def test_professional_user_can_access_dashboard():
    test_password = "MotDePasse-solide-2026"  # noqa: S105
    user = get_user_model().objects.create_user(
        username="professionnel",
        password=test_password,
        email="pro@example.com",
    )
    client = Client()
    client.force_login(user)

    response = client.get("/fr/espace-pro/")

    assert response.status_code == 200
    assert "Tableau de bord" in response.content.decode()


@pytest.mark.django_db
def test_professional_login_page_is_public():
    response = Client().get("/fr/espace-pro/connexion/")

    assert response.status_code == 200
    assert "Se connecter" in response.content.decode()
