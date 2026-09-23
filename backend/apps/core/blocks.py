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


class OrgPersonBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False, label="Photo")
    name = blocks.CharBlock(label="Nom")
    role = blocks.CharBlock(label="Fonction ou direction")


class OrgGroupBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre du groupe", help_text="Ex. : Directions sectorielles.")
    featured = blocks.BooleanBlock(
        required=False,
        label="Mettre en avant",
        help_text="Cartes plus grandes, pour la direction générale.",
    )
    members = blocks.ListBlock(OrgPersonBlock(), label="Personnes")


class OrgDirectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Direction")
    departments = blocks.ListBlock(
        blocks.CharBlock(label="Département"), required=False, label="Départements"
    )


class OrgStructureBlock(blocks.StructBlock):
    """Structure hiérarchique (gouvernance, DG, directions, départements), sans photo.

    Complète le bloc « Organigramme » (trombinoscope avec photos) en montrant l'arborescence
    complète de l'organisation, telle qu'elle existe même quand aucun nom n'est publié pour un
    poste. Entièrement modifiable depuis l'admin : ajouter, renommer ou réordonner les unités.
    """

    governance_title = blocks.CharBlock(label="Organe", default="Conseil d'Administration")
    governance_branches = blocks.ListBlock(
        blocks.CharBlock(label="Organe rattaché"),
        label="Organes rattachés au Conseil d'Administration",
        default=["Comités spécialisés", "Comité de direction"],
    )
    dg_title = blocks.CharBlock(label="Titre", default="Directeur Général")
    dg_attached = blocks.ListBlock(
        blocks.CharBlock(label="Unité"),
        label="Unités rattachées au Directeur Général",
        default=["Cabinet du DG", "Conseillers techniques"],
    )
    dg_cells = blocks.ListBlock(
        blocks.CharBlock(label="Cellule"), label="Cellules rattachées à la Direction générale"
    )
    secretariat_title = blocks.CharBlock(label="Titre", default="Secrétariat Général")
    secretariat_cells = blocks.ListBlock(
        blocks.CharBlock(label="Cellule"), label="Cellules du Secrétariat Général"
    )
    directions = blocks.ListBlock(OrgDirectionBlock(), label="Directions")
    regional_title = blocks.CharBlock(label="Ports régionaux", default="Ports régionaux (4)")

    class Meta:
        icon = "group"
        label = "Structure de l'organigramme"
        template = "core/blocks/org_structure.html"


class OrgChartBlock(blocks.StructBlock):
    """Organigramme : groupes de personnes avec photo, nom et fonction, tous modifiables."""

    groups = blocks.ListBlock(OrgGroupBlock(), label="Groupes")

    class Meta:
        icon = "group"
        label = "Organigramme"
        template = "core/blocks/org_chart.html"


class ContentStreamBlock(blocks.StreamBlock):
    """Bibliothèque de blocs disponible pour composer une page."""

    heading = HeadingBlock()
    paragraph = RichTextBlock()
    image = ImageBlock()
    callout = CalloutBlock()
    cta = CTABlock()
    table = TableBlock()
    org_chart = OrgChartBlock()
    org_structure = OrgStructureBlock()

    class Meta:
        block_counts: dict[str, Any] = {}
