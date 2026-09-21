"""Page éditoriale QSSE et RSE du Port."""

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from apps.core.blocks import ContentStreamBlock
from apps.core.seo import SocialMetadataMixin
from apps.qualite.models import Certification


class PageQSE(SocialMetadataMixin, Page):
    """Page Qualité, Sécurité, Sûreté et Environnement."""

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
        verbose_name = "Page QSSE / RSE"
        verbose_name_plural = "Pages QSSE / RSE"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["certifications"] = Certification.objects.all()
        return context
