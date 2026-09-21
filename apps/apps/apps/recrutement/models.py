"""Offres et page carrière du Port Autonome de Dakar."""

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from apps.core.blocks import ContentStreamBlock
from apps.core.seo import SocialMetadataMixin


@register_snippet
class Offre(models.Model):
    CONTRAT_CHOICES = [
        ("cdi", "CDI"),
        ("cdd", "CDD"),
        ("stage", "Stage"),
        ("alternance", "Alternance"),
    ]
    STATUT_CHOICES = [("ouverte", "Ouverte"), ("cloturee", "Clôturée")]

    title = models.CharField(max_length=180, verbose_name="Intitulé du poste")
    department = models.CharField(max_length=150, verbose_name="Direction / service")
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRAT_CHOICES,
        verbose_name="Type de contrat",
    )
    description = StreamField(ContentStreamBlock(), verbose_name="Description")
    publication_date = models.DateField(verbose_name="Date de publication")
    application_deadline = models.DateField(verbose_name="Date limite de candidature")
    status = models.CharField(
        max_length=12,
        choices=STATUT_CHOICES,
        default="ouverte",
        verbose_name="Statut",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("department"),
        FieldPanel("contract_type"),
        FieldPanel("description"),
        FieldPanel("publication_date"),
        FieldPanel("application_deadline"),
        FieldPanel("status"),
    ]

    class Meta:
        ordering = ["-publication_date", "title"]
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

    def __str__(self):
        return self.title


class RecruitmentIndexPage(SocialMetadataMixin, Page):
    """Page carrière présentant les offres ouvertes et la candidature."""

    intro = models.CharField(max_length=255, blank=True, verbose_name="Introduction")
    body = StreamField(ContentStreamBlock(), blank=True, verbose_name="Contenu")

    parent_page_types = ["cms.HomePage", "cms.StandardPage"]
    subpage_types: list[str] = []
    content_panels = (
        Page.content_panels
        + [FieldPanel("intro"), FieldPanel("body")]
        + SocialMetadataMixin.social_metadata_panels
    )

    class Meta:
        verbose_name = "Index recrutement"
        verbose_name_plural = "Index recrutement"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["offers"] = Offre.objects.filter(status="ouverte")
        return context
