"""Réglages transverses, modifiables depuis l'admin (Paramètres)."""

from django.db import models
from django.utils.translation import gettext as gettext_
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

DEFAULT_NAVIRES_EYEBROW = "Trafic maritime"
DEFAULT_NAVIRES_TITLE = "Mouvement des navires"
DEFAULT_NAVIRES_INTRO = "Suivez les arrivées, les escales à quai et les départs du port de Dakar."
DEFAULT_CROISIERES_EYEBROW = "Infos pratiques"
DEFAULT_CROISIERES_TITLE = "Escales de croisière"
DEFAULT_CROISIERES_INTRO = (
    "Le calendrier des paquebots attendus au Port Autonome de Dakar, avec leur poste "
    "à quai et leur consignataire."
)
DEFAULT_MARCHES_EYEBROW = "Transparence et commande publique"
DEFAULT_MARCHES_TITLE = "Marchés publics"
DEFAULT_MARCHES_INTRO = (
    "Consultez les appels d'offres, avis d'attribution et plans de passation du Port "
    "Autonome de Dakar."
)


@register_setting(icon="doc-full")
class ListHeaderSettings(BaseSiteSetting):
    """Titres et textes d'introduction des pages de listes (navires, croisières, marchés).

    Ces pages sont générées depuis la base de données (escales, croisières, appels d'offres) et
    n'ont donc pas de StreamField : ce réglage permet de modifier leur en-tête depuis l'admin,
    sans intervention d'un développeur. Ce réglage n'existe qu'en une seule langue (il n'est pas
    lié à une locale Wagtail) : `display()` traduit à la volée les valeurs restées au texte par
    défaut ; un texte personnalisé par un rédacteur est affiché tel quel, dans sa langue de saisie.
    """

    navires_eyebrow = models.CharField(
        "Sur-titre", max_length=120, default=DEFAULT_NAVIRES_EYEBROW, blank=True
    )
    navires_title = models.CharField(
        "Titre", max_length=140, default=DEFAULT_NAVIRES_TITLE, blank=True
    )
    navires_intro = models.TextField(
        "Texte d'introduction", default=DEFAULT_NAVIRES_INTRO, blank=True
    )

    croisieres_eyebrow = models.CharField(
        "Sur-titre", max_length=120, default=DEFAULT_CROISIERES_EYEBROW, blank=True
    )
    croisieres_title = models.CharField(
        "Titre", max_length=140, default=DEFAULT_CROISIERES_TITLE, blank=True
    )
    croisieres_intro = models.TextField(
        "Texte d'introduction", default=DEFAULT_CROISIERES_INTRO, blank=True
    )

    marches_eyebrow = models.CharField(
        "Sur-titre", max_length=120, default=DEFAULT_MARCHES_EYEBROW, blank=True
    )
    marches_title = models.CharField(
        "Titre", max_length=140, default=DEFAULT_MARCHES_TITLE, blank=True
    )
    marches_intro = models.TextField(
        "Texte d'introduction", default=DEFAULT_MARCHES_INTRO, blank=True
    )

    _TRANSLATABLE_DEFAULTS = {
        "navires_eyebrow": DEFAULT_NAVIRES_EYEBROW,
        "navires_title": DEFAULT_NAVIRES_TITLE,
        "navires_intro": DEFAULT_NAVIRES_INTRO,
        "croisieres_eyebrow": DEFAULT_CROISIERES_EYEBROW,
        "croisieres_title": DEFAULT_CROISIERES_TITLE,
        "croisieres_intro": DEFAULT_CROISIERES_INTRO,
        "marches_eyebrow": DEFAULT_MARCHES_EYEBROW,
        "marches_title": DEFAULT_MARCHES_TITLE,
        "marches_intro": DEFAULT_MARCHES_INTRO,
    }

    def display(self, field_name: str) -> str:
        """Valeur du champ, traduite si elle est restée au texte par défaut (voir docstring)."""
        value = getattr(self, field_name)
        default = self._TRANSLATABLE_DEFAULTS[field_name]
        return gettext_(default) if value == default else value

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
