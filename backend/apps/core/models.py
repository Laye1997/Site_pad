"""Réglages transverses, modifiables depuis l'admin (Paramètres)."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting(icon="doc-full")
class ListHeaderSettings(BaseSiteSetting):
    """Titres et textes d'introduction des pages de listes (navires, croisières, marchés).

    Ces pages sont générées depuis la base de données (escales, croisières, appels d'offres) et
    n'ont donc pas de StreamField : ce réglage permet de modifier leur en-tête depuis l'admin,
    sans intervention d'un développeur.
    """

    navires_eyebrow = models.CharField(
        "Sur-titre", max_length=120, default="Trafic maritime", blank=True
    )
    navires_title = models.CharField(
        "Titre", max_length=140, default="Mouvement des navires", blank=True
    )
    navires_intro = models.TextField(
        "Texte d'introduction",
        default="Suivez les arrivées, les escales à quai et les départs du port de Dakar.",
        blank=True,
    )

    croisieres_eyebrow = models.CharField(
        "Sur-titre", max_length=120, default="Infos pratiques", blank=True
    )
    croisieres_title = models.CharField(
        "Titre", max_length=140, default="Escales de croisière", blank=True
    )
    croisieres_intro = models.TextField(
        "Texte d'introduction",
        default=(
            "Le calendrier des paquebots attendus au Port Autonome de Dakar, avec leur poste "
            "à quai et leur consignataire."
        ),
        blank=True,
    )

    marches_eyebrow = models.CharField(
        "Sur-titre", max_length=120, default="Transparence et commande publique", blank=True
    )
    marches_title = models.CharField("Titre", max_length=140, default="Marchés publics", blank=True)
    marches_intro = models.TextField(
        "Texte d'introduction",
        default=(
            "Consultez les appels d'offres, avis d'attribution et plans de passation du Port "
            "Autonome de Dakar."
        ),
        blank=True,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("navires_eyebrow"),
                FieldPanel("navires_title"),
                FieldPanel("navires_intro"),
            ],
            heading="Mouvement des navires",
        ),
        MultiFieldPanel(
            [
                FieldPanel("croisieres_eyebrow"),
                FieldPanel("croisieres_title"),
                FieldPanel("croisieres_intro"),
            ],
            heading="Croisières",
        ),
        MultiFieldPanel(
            [
                FieldPanel("marches_eyebrow"),
                FieldPanel("marches_title"),
                FieldPanel("marches_intro"),
            ],
            heading="Marchés publics",
        ),
    ]

    class Meta:
        verbose_name = _("Textes des pages de listes")
