import io
from html import escape

import pytest
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.test import Client
from PIL import Image as PILImage
from wagtail.images.models import Image
from wagtail.models import Page, Site

from apps.services.models import ServiceIndexPage, ServicePage

SERVICE_TITLES = [
    "Accueil des navires",
    "Trafic passagers",
    "Marchandises",
    "Obtention d'agrément",
]


def create_image():
    image = PILImage.new("RGB", (100, 60), "#0d7ea4")
    image_file = io.BytesIO()
    image.save(image_file, format="PNG")
    image_file.seek(0)
    return Image.objects.create(
        title="Illustration du service",
        file=ImageFile(image_file, name="service.png"),
    )


@pytest.fixture
def service_index(db):
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    index = ServiceIndexPage(title="Services", intro="Les services du port.")
    root.add_child(instance=index)
    index.save_revision().publish()
    for title in SERVICE_TITLES:
        service = ServicePage(title=title, summary=f"Résumé de {title}.")
        index.add_child(instance=service)
        service.save_revision().publish()
    return index


@pytest.mark.django_db
def test_service_index_lists_four_key_services(service_index):
    response = Client().get(service_index.url)

    assert response.status_code == 200
    content = response.content.decode()
    for title in SERVICE_TITLES:
        assert escape(title) in content
    assert content.count('class="service-card"') == 4


@pytest.mark.django_db
def test_service_page_renders_stream_content_and_accessible_illustration(service_index):
    service = ServicePage(
        title="Accueil des navires",
        summary="Une escale préparée et accompagnée.",
        body=[("heading", {"text": "Préparer votre escale", "level": "h2"})],
        illustration=create_image(),
        illustration_alt="Navire porte-conteneurs à quai au Port de Dakar",
    )
    service_index.add_child(instance=service)
    service.save_revision().publish()

    response = Client().get(service.url)

    assert response.status_code == 200
    assert "Préparer votre escale" in response.content.decode()
    assert 'alt="Navire porte-conteneurs à quai au Port de Dakar"' in response.content.decode()


@pytest.mark.django_db
def test_service_illustration_requires_alt_text():
    service = ServicePage(
        title="Marchandises",
        summary="Une offre logistique complète.",
        illustration=create_image(),
    )

    with pytest.raises(ValidationError) as error:
        service.full_clean()

    assert "illustration_alt" in error.value.message_dict
