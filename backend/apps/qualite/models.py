"""
Gestion des certifications ISO du Port (9001 / 14001 / 45001).

Modélisées comme snippets Wagtail : réutilisables sur n'importe quelle page,
datées et versionnées, avec le document officiel attaché.
"""

from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Certification(models.Model):
    REFERENTIELS = [
        ("iso9001", "ISO 9001 — Qualité"),
        ("iso14001", "ISO 14001 — Environnement"),
        ("iso45001", "ISO 45001 — Santé & sécurité au travail"),
    ]

    referentiel = models.CharField(max_length=20, choices=REFERENTIELS, verbose_name="Référentiel")
    perimetre = models.CharField(max_length=255, verbose_name="Périmètre certifié")
    organisme = models.CharField(max_length=120, verbose_name="Organisme certificateur")
    numero = models.CharField(max_length=80, blank=True, verbose_name="N° de certificat")
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_validite = models.DateField(verbose_name="Valide jusqu'au")
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Certificat (PDF)",
    )

    visual = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Aperçu du certificat (image)",
    )

    panels = [
        FieldPanel("referentiel"),
        FieldPanel("perimetre"),
        FieldPanel("organisme"),
        FieldPanel("numero"),
        FieldPanel("date_emission"),
        FieldPanel("date_validite"),
        FieldPanel("document"),
        FieldPanel("visual"),
    ]

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["referentiel"]

    def __str__(self) -> str:
        return f"{self.get_referentiel_display()} — {self.perimetre}"

    @property
    def est_valide(self) -> bool:
        return self.date_validite >= timezone.now().date()
