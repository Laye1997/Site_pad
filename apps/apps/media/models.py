"""Pages éditoriales de l'espace média."""

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.models import Image
from wagtail.models import Page

from apps.core.blocks import ContentStreamBlock
from apps.core.seo import SocialMetadataMixin


class MediaIndexPage(SocialMetadataMixin, Page):
    """Index paginé des actualités et communiqués du port."""

    intro = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Introduction",
    )

    parent_page_types = ["cms.HomePage", "cms.StandardPage"]
    subpage_types = ["media.ArticlePage"]
    content_panels = (
        Page.content_panels + [FieldPanel("intro")] + SocialMetadataMixin.social_metadata_panels
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        category = request.GET.get("categorie", "tous")
        categories = dict(ArticlePage.CATEGORY_CHOICES)
        active_category = category if category in categories else "tous"
        articles = ArticlePage.objects.live().public().child_of(self)
        if active_category != "tous":
            articles = articles.filter(category=active_category)
        paginator = Paginator(articles.order_by("-publication_date", "-first_published_at"), 9)
        context["articles"] = paginator.get_page(request.GET.get("page"))
        context["categories"] = {"tous": "Tous", **categories}
        context["active_category"] = active_category
        return context

    def serve(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") == "true":
            return render(request, "media/partials/article_grid.html", self.get_context(request))
        return super().serve(request, *args, **kwargs)

    class Meta:
        verbose_name = "Index média"
        verbose_name_plural = "Index média"


class ArticlePage(SocialMetadataMixin, Page):
    """Article, communiqué ou contenu photo publié dans l'espace média."""

    CATEGORY_CHOICES = [
        ("actualite", "Actualité"),
        ("communique", "Communiqué"),
        ("note", "Note aux usagers"),
        ("evenement", "Événement"),
        ("photos", "Photos et vidéos"),
    ]

    summary = models.CharField(max_length=255, verbose_name="Résumé")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="actualite",
        verbose_name="Catégorie",
    )
    publication_date = models.DateField(verbose_name="Date de publication")
    body = StreamField(ContentStreamBlock(), blank=True, verbose_name="Contenu")
    cover_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="media_articles",
        verbose_name="Image principale",
    )
    cover_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Texte alternatif de l'image principale",
        help_text="Obligatoire lorsqu'une image principale est sélectionnée.",
    )

    parent_page_types = ["media.MediaIndexPage"]
    subpage_types: list[str] = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related"] = list(
            ArticlePage.objects.live()
            .public()
            .exclude(pk=self.pk)
            .exclude(category="note")
            .order_by("-publication_date")[:3]
        )
        return context

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("summary"),
            FieldPanel("category"),
            FieldPanel("publication_date"),
            FieldPanel("cover_image"),
            FieldPanel("cover_alt"),
            FieldPanel("body"),
        ]
        + SocialMetadataMixin.social_metadata_panels
    )

    class Meta:
        verbose_name = "Article média"
        verbose_name_plural = "Articles média"
        ordering = ["-publication_date", "-first_published_at"]

    def clean(self):
        super().clean()
        if self.cover_image and not self.cover_alt.strip():
            raise ValidationError(
                {"cover_alt": "Le texte alternatif est obligatoire avec une image."}
            )
