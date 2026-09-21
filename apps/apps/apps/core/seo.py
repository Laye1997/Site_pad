"""Champs SEO communs aux pages éditoriales."""

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel


class SocialMetadataMixin(models.Model):
    """Ajoute une image de partage social aux pages du site."""

    share_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image de partage",
        help_text="Image utilisée dans les aperçus de partage (Open Graph).",
    )
    share_image_alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Texte alternatif de l'image de partage",
        help_text="Obligatoire lorsqu'une image de partage est sélectionnée.",
    )

    card_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Photo de la rubrique",
        help_text="Photo affichée sur la carte de cette rubrique (accueil). Décorative.",
    )

    social_metadata_panels = [
        FieldPanel("card_image"),
        FieldPanel("share_image"),
        FieldPanel("share_image_alt"),
    ]

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.share_image and not self.share_image_alt.strip():
            raise ValidationError(
                {"share_image_alt": "Le texte alternatif est obligatoire avec une image."}
            )
