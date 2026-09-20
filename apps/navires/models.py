"""Modèles métier du mouvement des navires."""

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Escale(models.Model):
    """Escale maritime enregistrée dans le port."""

    TYPE_CHOICES = [
        ("conteneur", "Conteneur"),
        ("cargo", "Cargo"),
        ("vrac", "Vrac"),
        ("passagers", "Passagers"),
        ("croisiere", "Cruise"),
    ]

    STATUT_CHOICES = [
        ("attendu", "Attendu"),
        ("a_quai", "À quai"),
        ("parti", "Parti"),
    ]

    navire = models.CharField(max_length=120, verbose_name="Nom du navire")
    type_navire = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="conteneur",
        verbose_name="Type de navire",
    )
    pavillon = models.CharField(max_length=80, verbose_name="Pavillon")
    provenance = models.CharField(max_length=120, verbose_name="Provenance")
    destination = models.CharField(max_length=120, verbose_name="Destination")
    quai = models.CharField(max_length=80, blank=True, verbose_name="Quai")
    date_arrivee = models.DateField(verbose_name="Date d'arrivée")
    date_depart = models.DateField(null=True, blank=True, verbose_name="Date de départ")
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="attendu",
        verbose_name="Statut",
    )
    consignataire = models.CharField(max_length=140, blank=True, verbose_name="Consignataire")
    updated_at = models.DateTimeField(
        auto_now=True, null=True, editable=False, verbose_name="Dernière mise à jour"
    )

    panels = [
        FieldPanel("navire"),
        FieldPanel("type_navire"),
        FieldPanel("pavillon"),
        FieldPanel("provenance"),
        FieldPanel("destination"),
        FieldPanel("quai"),
        FieldPanel("date_arrivee"),
        FieldPanel("date_depart"),
        FieldPanel("statut"),
        FieldPanel("consignataire"),
    ]

    class Meta:
        verbose_name = "Escale"
        verbose_name_plural = "Escales"
        ordering = ["date_arrivee", "navire"]

    def __str__(self) -> str:
        return f"{self.navire} — {self.get_statut_display()}"
