"""Modèles de pages éditoriales (Wagtail)."""

from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from apps.cms.home_blocks import HomeSectionsBlock, default_home_sections
from apps.core.blocks import ContentStreamBlock
from apps.core.seo import SocialMetadataMixin


class KeyFigureBlock(blocks.StructBlock):
    """Chiffre clé affiché sur l'accueil (valeur saisie et sourcée par la rédaction)."""

    value = blocks.CharBlock(max_length=20, label="Valeur", help_text="Ex. : 22,5 M")
    label = blocks.CharBlock(max_length=80, label="Libellé")
    source = blocks.CharBlock(required=False, max_length=120, label="Source / année")

    class Meta:
        icon = "order"
        label = "Chiffre clé"


class HomePage(SocialMetadataMixin, Page):
    """Page d'accueil du site."""

    hero_title = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Titre principal",
        help_text="Unique h1 de la page. Valeur par défaut si vide.",
    )
    intro = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Accroche",
        help_text="Phrase d'accroche affichée dans l'en-tête.",
    )
    key_figures = StreamField(
        [("figure", KeyFigureBlock())],
        blank=True,
        max_num=6,
        verbose_name="Chiffres clés",
        help_text="Bandeau de chiffres officiels (6 maximum). Masqué s'il est vide.",
    )
    sections = StreamField(
        HomeSectionsBlock(),
        blank=True,
        verbose_name="Sections de l'accueil",
        help_text=(
            "Composez l'accueil : ajoutez, déplacez ou supprimez les sections. "
            "Si vide, la composition par défaut du site est affichée."
        ),
    )
    body = StreamField(
        ContentStreamBlock(),
        blank=True,
        verbose_name="Contenu libre (sous les sections)",
    )

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("sections"),
            FieldPanel("body"),
        ]
        + SocialMetadataMixin.social_metadata_panels
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_pages"] = self.get_children().live().public().in_menu().specific()
        context["home_sections"] = self.effective_sections()
        return context

    def effective_sections(self):
        """Sections enregistrées par les rédacteurs, sinon composition par défaut."""
        if len(self.sections):
            return self.sections
        return HomeSectionsBlock().to_python(
            [{"type": kind, "value": value} for kind, value in default_home_sections(self)]
        )

    class Meta:
        verbose_name = "Page d'accueil"


class StandardPage(SocialMetadataMixin, Page):
    """Page institutionnelle générique composée de blocs modulaires."""

    MODULE_CHOICES = [
        ("", "Aucun"),
        ("marches:appel_offres", "Liste : appels d'offres"),
        ("marches:avis_attribution", "Liste : avis d'attribution"),
        ("marches:plan_passation", "Liste : plan de passation"),
        ("marches:manifestation_interet", "Liste : manifestations d'intérêt"),
        ("articles:actualite", "Liste : actualités"),
        ("articles:communique", "Liste : communiqués de presse"),
        ("articles:photos", "Liste : photothèque / vidéothèque"),
        ("partners:strategique", "Partenaires stratégiques"),
        ("partners:institutionnel", "Partenaires institutionnels"),
        ("partners:international", "Partenaires internationaux"),
        ("key_figures", "Chiffres clés de l'accueil"),
        ("subpages", "Cartes vers les sous-pages"),
    ]

    module = models.CharField(
        max_length=40,
        choices=MODULE_CHOICES,
        blank=True,
        default="",
        verbose_name="Module dynamique",
        help_text="Affiche automatiquement une liste sous le contenu de la page.",
    )

    body = StreamField(
        ContentStreamBlock(),
        blank=True,
        verbose_name="Contenu",
    )

    content_panels = (
        Page.content_panels
        + [FieldPanel("body"), FieldPanel("module")]
        + SocialMetadataMixin.social_metadata_panels
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(self._module_context())
        parent = self.get_parent().specific
        # Une page de premier niveau (fille de l'accueil) est elle-même la rubrique : son menu
        # latéral liste ses sous-pages, pas tout le site.
        section_page = self if isinstance(parent, HomePage) else parent
        context["section_page"] = section_page
        context["section_children"] = section_page.get_children().live().public().specific()
        context["section_grandchildren"] = {
            child.id: child.get_children().live().public().specific()
            for child in context["section_children"]
        }
        return context

    def _module_context(self) -> dict:
        """Données du module choisi (imports locaux : pas de dépendance croisée au chargement)."""
        kind, _, arg = self.module.partition(":")
        if kind == "marches":
            from apps.marches.models import AppelOffre

            return {"module_marches": AppelOffre.objects.filter(type_marche=arg)}
        if kind == "articles":
            from apps.media.models import ArticlePage

            return {
                "module_articles": ArticlePage.objects.live()
                .public()
                .filter(category=arg)
                .order_by("-publication_date")[:12]
            }
        if kind == "partners":
            return {
                "module_partners": Partner.objects.filter(is_active=True, category=arg),
            }
        if kind == "key_figures":
            home = HomePage.objects.first()
            return {"module_figures": home.key_figures if home else []}
        if kind == "subpages":
            return {"module_subpages": self.get_children().live().public().specific()}
        return {}

    class Meta:
        verbose_name = "Page standard"


@register_snippet
class Partner(models.Model):
    """Partenaire affiché sur l'accueil (snippet réutilisable, géré sans développeur)."""

    CATEGORY_CHOICES = [
        ("", "Non classé"),
        ("strategique", "Stratégique"),
        ("institutionnel", "Institutionnel"),
        ("international", "International"),
    ]

    name = models.CharField(max_length=120, verbose_name="Nom")
    category = models.CharField(
        max_length=16, choices=CATEGORY_CHOICES, blank=True, default="", verbose_name="Catégorie"
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="Logo",
    )
    url = models.URLField(blank=True, verbose_name="Site web")
    position = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Affiché sur le site")

    panels = [
        FieldPanel("name"),
        FieldPanel("category"),
        FieldPanel("logo"),
        FieldPanel("url"),
        FieldPanel("position"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ["position", "name"]

    def __str__(self) -> str:
        return self.name
