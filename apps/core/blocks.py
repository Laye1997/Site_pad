"""
Blocs de contenu réutilisables (StreamField).

Ces blocs constituent la « modularité de contenu » (niveau 2) : un rédacteur
compose une page en empilant des blocs, sans intervention d'un développeur.
"""

from typing import Any

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(label="Titre")
    level = blocks.ChoiceBlock(
        choices=[("h2", "Titre 2"), ("h3", "Titre 3")],
        default="h2",
        label="Niveau",
    )

    class Meta:
        icon = "title"
        label = "Titre"
        template = "core/blocks/heading.html"


class RichTextBlock(blocks.RichTextBlock):
    class Meta:
        icon = "doc-full"
        label = "Texte enrichi"
        template = "core/blocks/richtext.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Image")
    caption = blocks.CharBlock(required=False, label="Légende")
    alt = blocks.CharBlock(
        required=True,
        label="Texte alternatif",
        help_text="Description de l'image pour l'accessibilité (obligatoire).",
    )

    class Meta:
        icon = "image"
        label = "Image"
        template = "core/blocks/image.html"


class CalloutBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    body = blocks.TextBlock(label="Contenu")

    class Meta:
        icon = "help"
        label = "Encadré"
        template = "core/blocks/callout.html"


class CTABlock(blocks.StructBlock):
    label = blocks.CharBlock(label="Libellé du bouton")
    url = blocks.URLBlock(label="Lien")

    class Meta:
        icon = "link"
        label = "Bouton d'action"
        template = "core/blocks/cta.html"


class TableBlock(blocks.StructBlock):
    headers = blocks.ListBlock(blocks.CharBlock(label="En-tête"), label="En-têtes")
    rows = blocks.ListBlock(
        blocks.ListBlock(blocks.CharBlock(label="Cellule"), label="Ligne"),
        label="Lignes",
    )

    class Meta:
        icon = "list-ul"
        label = "Tableau accessible"
        template = "core/blocks/table.html"


class ContentStreamBlock(blocks.StreamBlock):
    """Bibliothèque de blocs disponible pour composer une page."""

    heading = HeadingBlock()
    paragraph = RichTextBlock()
    image = ImageBlock()
    callout = CalloutBlock()
    cta = CTABlock()
    table = TableBlock()

    class Meta:
        block_counts: dict[str, Any] = {}
