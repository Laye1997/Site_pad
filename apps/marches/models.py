"""Marchés publics publiés par le Port Autonome de Dakar."""

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class AppelOffre(models.Model):
    TYPE_CHOICES = [
        ("appel_offres", "Appel d'offres"),
        ("avis_attribution", "Avis d'attribution"),
        ("plan_passation", "Plan de passation"),
    ]
    STATUT_CHOICES = [
        ("ouvert", "Ouvert"),
        ("cloture", "Clôturé"),
        ("attribue", "Attribué"),
    ]

    objet = models.CharField(max_length=255, verbose_name="Objet")
    reference = models.CharField(max_length=80, unique=True, verbose_name="Référence")
    type_marche = models.CharField(
        max_length=24,
        choices=TYPE_CHOICES,
        default="appel_offres",
        verbose_name="Type de publication",
    )
    date_publication = models.DateField(verbose_name="Date de publication")
    date_limite = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date limite de dépôt",
    )
    documents = models.ManyToManyField(
        "wagtaildocs.Document",
        blank=True,
        related_name="marches_publics",
        verbose_name="Documents attachés",
    )
    statut = models.CharField(
        max_length=12,
        choices=STATUT_CHOICES,
        default="ouvert",
        verbose_name="Statut",
    )

    panels = [
        FieldPanel("objet"),
        FieldPanel("reference"),
        FieldPanel("type_marche"),
        FieldPanel("date_publication"),
        FieldPanel("date_limite"),
        FieldPanel("documents"),
        FieldPanel("statut"),
    ]

    class Meta:
        verbose_name = "Marché public"
        verbose_name_plural = "Marchés publics"
        ordering = ["-date_publication", "reference"]

    def __str__(self) -> str:
        return f"{self.reference} — {self.objet}"
