import datetime as dt

import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from wagtail.models import Page, Site

from apps.recrutement.models import Offre, RecruitmentIndexPage


@pytest.fixture
def recruitment_page(db):
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    page = RecruitmentIndexPage(title="Recrutement", intro="Rejoignez le PAD.")
    root.add_child(instance=page)
    page.save_revision().publish()
    Offre.objects.create(
        title="Responsable opérations portuaires",
        department="Direction de l'exploitation",
        contract_type="cdi",
        description=[("paragraph", "Description du poste")],
        publication_date=dt.date(2026, 9, 1),
        application_deadline=dt.date(2026, 10, 1),
        status="ouverte",
    )
    return page


@pytest.mark.django_db
def test_recruitment_page_lists_open_offers(recruitment_page):
    response = Client().get(recruitment_page.url)

    assert response.status_code == 200
    assert "Responsable opérations portuaires" in response.content.decode()
    assert "/recrutement/postuler/" in response.content.decode()


@pytest.mark.django_db
def test_application_rejects_invalid_cv():
    response = Client().post(
        "/fr/recrutement/postuler/",
        {
            "name": "Awa Ndiaye",
            "email": "awa@example.com",
            "message": "Je souhaite rejoindre le PAD.",
            "cv": SimpleUploadedFile("cv.txt", b"not a cv", content_type="text/plain"),
        },
    )

    assert response.status_code == 200
    assert "PDF ou DOCX" in response.content.decode()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_application_sends_email_with_valid_pdf():
    response = Client().post(
        "/fr/recrutement/postuler/",
        {
            "name": "Awa Ndiaye",
            "email": "awa@example.com",
            "message": "Je souhaite rejoindre le PAD.",
            "cv": SimpleUploadedFile("cv.pdf", b"%PDF-test", content_type="application/pdf"),
        },
    )

    assert response.status_code == 302
    assert response.url == "/fr/recrutement/confirmation/"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].attachments[0][0] == "cv.pdf"
