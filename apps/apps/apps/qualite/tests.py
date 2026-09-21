import datetime as dt

import pytest
from django.core.management import call_command
from django.test import Client
from wagtail.models import Page, Site

from apps.qualite.models import Certification
from apps.qualite.pages import PageQSE


@pytest.mark.django_db
def test_page_qse_displays_certifications():
    root = Page.objects.get(depth=1)
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={"root_page": root, "is_default_site": True},
    )
    Certification.objects.create(
        referentiel="iso9001",
        perimetre="Management de la qualité",
        organisme="Bureau Veritas",
        date_emission=dt.date(2025, 1, 1),
        date_validite=dt.date(2027, 1, 1),
    )
    page = PageQSE(title="QSSE et RSE", intro="Notre démarche.")
    root.add_child(instance=page)
    page.save_revision().publish()

    response = Client().get(page.url)

    assert response.status_code == 200
    assert "Management de la qualité" in response.content.decode()
    assert "Certification en cours de validité" in response.content.decode()


@pytest.mark.django_db
def test_certification_alert_command_lists_expiring_certificates(capsys):
    Certification.objects.create(
        referentiel="iso14001",
        perimetre="Environnement",
        organisme="Bureau Veritas",
        date_emission=dt.date(2025, 1, 1),
        date_validite=dt.date.today() + dt.timedelta(days=30),
    )

    call_command("certifications_a_alerter")

    assert "ISO 14001" in capsys.readouterr().out
