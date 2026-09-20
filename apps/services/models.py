"""Pages Wagtail présentant l'offre de service du port."""

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.models import Image
from wagtail.models import Page

from apps.core.blocks import ContentStreamBlock
from apps.core.seo import SocialMetadataMixin


class ServiceIndexPage(SocialMetadataMixin, Page):
    """Page d'index qui présente les services disponibles."""

    intro = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Introduction",
        help_text="Phrase de présentation affichée au-dessus de la liste.",
    )

    parent_page_types = ["cms.HomePage", "cms.StandardPage"]
    subpage_types = ["services.ServicePage"]

    content_panels = (
        Page.content_panels + [FieldPanel("intro")] + SocialMetadataMixin.social_metadata_panels
    )

    class Meta:
        verbose_name = "Index des services"
        verbose_name_plural = "Index des services"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["services"] = self.get_children().live().public().specific()
        return context


class ServicePage(SocialMetadataMixin, Page):
    """Page détaillant un service proposé par le port."""

    summary = models.CharField(
        max_length=255,
        verbose_name="Résumé",
        help_text="Résumé court affiché dans la liste des services.",
    )
    body = StreamField(
        ContentStreamBlock(),
        blank=True,
        verbose_name="Contenu",
    )
    illustration = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_pages",
        verbose_name="Illustration",
    )
    illustration_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Texte alternatif de l'illustration",
        help_text="Obligatoire lorsqu'une illustration est sélectionnée.",
    )

    parent_page_types = ["services.ServiceIndexPage"]
    subpage_types = ["services.ServicePage"]

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("summary"),
            FieldPanel("body"),
            FieldPanel("illustration"),
            FieldPanel("illustration_alt"),
        ]
        + SocialMetadataMixin.social_metadata_panels
    )

    class Meta:
        verbose_name = "Page de service"
        verbose_name_plural = "Pages de service"

    def get_context(self, request, *args, **kwargs):
        """Fil d'Ariane et menu latéral : la rubrique (ou la page elle-même) et ses sous-pages."""
        context = super().get_context(request, *args, **kwargs)
        parent = self.get_parent().specific
        section = parent if isinstance(parent, ServicePage) else self
        context["section"] = section
        context["subnav"] = list(section.get_children().live().public().specific())
        context["breadcrumbs"] = [
            page
            for page in self.get_ancestors().live().specific()
            if page.depth > 2  # sans la racine et l'accueil
        ]
        return context

    def clean(self):
        super().clean()
        if self.illustration and not self.illustration_alt.strip():
            raise ValidationError(
                {"illustration_alt": "Le texte alternatif est obligatoire avec une illustration."}
            )
