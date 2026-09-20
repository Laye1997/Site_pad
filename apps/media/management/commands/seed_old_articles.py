"""Reprend deux articles de l'ancien site : « Les orientations annoncées » et « COLOVAC 2026 ».

Textes et photos viennent de portdakar.sn. Les pages d'origine n'affichent PAS de date de
publication : les dates ci-dessous sont provisoires et à confirmer par la rédaction.
Idempotent. Nécessite la page « Espace média » (commande seed_site_structure).
"""

import datetime as dt
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from wagtail.images.models import Image
from wagtail.rich_text import RichText

from apps.media.management.commands.older_articles_data import OLDER
from apps.media.models import ArticlePage, MediaIndexPage

SOURCE = Path(settings.BASE_DIR) / "static" / "img" / "origine"

ORIENTATIONS = [
    "Une gouvernance moderne, rigoureuse et transparente",
    "La modernisation des infrastructures et la mise en place de dispositifs anti-congestion",
    "La simplification des procédures par la digitalisation intégrale des services aux usagers",
    "Le dialogue avec les acteurs portuaires et le renforcement du capital humain",
    "L'optimisation des ressources et des actifs de la Société nationale",
    "La prise en compte des besoins de l'hinterland et des pays de la sous-région",
    "L'accélération des travaux du port multifonctionnel de Ndayane",
    "L'examen d'une extension des horaires de certains services",
]

# Visuels de l'article « Les orientations annoncées » : le texte est transcrit ci-dessus.
DG_VISUALS = [
    ("dg1.jpeg", "Visuel n° 1 : orientations 1 et 2, présentées par M. Doune Pathé MBENGUE."),
    ("dg2.jpeg", "Visuel n° 2 : orientations 3 et 4, présentées par M. Doune Pathé MBENGUE."),
    ("dg3.jpeg", "Visuel n° 3 : orientations 5 et 6, présentées par M. Doune Pathé MBENGUE."),
    (
        "dg4.jpeg",
        "Visuel n° 4 : orientations 7 et 8, inscrites dans la vision Sénégal 2050, "
        "présentées par M. Doune Pathé MBENGUE.",
    ),
]

COLOVAC_PHOTOS = [
    (
        "1_0.jpeg",
        "Le Directeur général entouré des enfants de la colonie de vacances en tenue bleue.",
    ),
    (
        "2_1.jpeg",
        "Photo de groupe devant la Direction générale du Port Autonome de Dakar, avec la "
        "banderole de la colonie de vacances.",
    ),
    ("3.jpeg", "Des enfants portant casquettes et tenues bleues de la colonie de vacances."),
    ("4.jpeg", "Des enfants et des accompagnateurs lors du départ de la colonie."),
    ("5.jpeg", "Des participants et des responsables du port lors de la cérémonie."),
    ("7.jpeg", "Des enfants de la colonie de vacances écoutant une allocution."),
    ("8.jpeg", "Un responsable s'adressant aux enfants réunis pour le départ."),
    ("9.jpeg", "Un responsable du port échangeant avec les enfants de la colonie."),
    ("10.jpeg", "Des responsables et des enfants réunis devant le bâtiment du port."),
]


def _p(text):
    return ("paragraph", RichText(f"<p>{text}</p>"))


class Command(BaseCommand):
    help = "Crée les articles « Les orientations annoncées » et « COLOVAC 2026 » (idempotent)."

    def handle(self, *args, **options):
        index = MediaIndexPage.objects.first()
        if index is None:
            raise CommandError("Page « Espace média » introuvable : lancez seed_site_structure.")
        self._orientations(index)
        self._colovac(index)
        for item in OLDER:
            self._older(index, item)

    def _older(self, index, item):
        title = item["title"]
        if ArticlePage.objects.filter(title=title).exists():
            return
        body = [_p(text) for text in item["paragraphs"]]
        if item.get("list"):
            items = "".join(f"<li>{text}</li>" for text in item["list"])
            body.append(_p(f"<b>{item['list_title']}</b>"))
            body.append(("paragraph", RichText(f"<ul>{items}</ul>")))
        images = [self._image(name, title[:60]) for name, _ in item["photos"]]
        for image, (_, alt) in zip(images[1:], item["photos"][1:], strict=True):
            body.append(("image", {"image": image, "caption": "", "alt": alt}))
        self._create(
            index,
            title,
            item["summary"],
            item["category"],
            item["date"],
            images[0],
            item["photos"][0][1],
            body,
        )

    def _orientations(self, index):
        title = "Les orientations annoncées"
        if ArticlePage.objects.filter(title=title).exists():
            return
        items = "".join(f"<li>{text}</li>" for text in ORIENTATIONS)
        body = [
            _p(
                "Le Directeur général, M. Doune Pathé MBENGUE, a présenté les orientations "
                "suivantes :"
            ),
            ("paragraph", RichText(f"<ol>{items}</ol>")),
            _p(
                "Ces orientations s'inscrivent dans la vision Sénégal 2050 et dans l'ambition "
                "d'un hub logistique intégré."
            ),
        ]
        images = [self._image(name, title) for name, _ in DG_VISUALS]
        for image, (_, alt) in zip(images, DG_VISUALS, strict=True):
            body.append(("image", {"image": image, "caption": "", "alt": alt}))
        self._create(
            index,
            title,
            "Le Directeur général présente huit orientations, inscrites dans la vision Sénégal "
            "2050 et dans l'ambition d'un hub logistique intégré.",
            "actualite",
            dt.date(2026, 8, 18),
            images[0],
            DG_VISUALS[0][1],
            body,
        )

    def _colovac(self, index):
        title = "COLOVAC 2026"
        if ArticlePage.objects.filter(title=title).exists():
            return
        body = [
            _p(
                "Le Port Autonome de Dakar a organisé un événement festif marquant le départ de sa "
                "colonie de vacances officielle 2026. Doune Pathé Mbengue, nouveau Directeur "
                "général, a assisté à cette première sortie officielle en son honneur."
            ),
            _p(
                "Il a salué une initiative précieuse pour l'épanouissement des enfants et la "
                "cohésion de la famille portuaire, tout en réaffirmant son souhait d'ancrer cette "
                "action dans la durée pour garantir un climat social harmonieux."
            ),
            _p(
                "Le programme souligne l'engagement de l'institution envers la jeunesse, la "
                "solidarité et le bien-être des familles des collaborateurs. La cérémonie "
                "incarnait « une vision tournée vers l'écoute, la proximité et la continuité, "
                "dans un esprit de confiance et de responsabilité. »"
            ),
        ]
        images = [self._image(name, title) for name, _ in COLOVAC_PHOTOS]
        for image, (_, alt) in zip(images[1:], COLOVAC_PHOTOS[1:], strict=True):
            body.append(("image", {"image": image, "caption": "", "alt": alt}))
        self._create(
            index,
            title,
            "Revivez en images les temps forts du départ de la colonie de vacances COLOVAC "
            "PAD2026. Une cérémonie placée sous le signe de la joie et du partage, célébrant "
            "« L'amitié, valeur africaine et olympique ».",
            "evenement",
            dt.date(2026, 8, 28),
            images[0],
            COLOVAC_PHOTOS[0][1],
            body,
        )

    def _create(self, index, title, summary, category, date, cover, cover_alt, body):
        article = ArticlePage(
            title=title,
            summary=summary,
            category=category,
            publication_date=date,
            cover_image=cover,
            cover_alt=cover_alt,
            body=body,
        )
        index.add_child(instance=article)
        article.save_revision().publish()
        self.stdout.write(f"Article créé : {article.url}")

    def _image(self, filename, title):
        with (SOURCE / filename).open("rb") as handle:
            image = Image(title=f"{title} — {filename}")
            image.file.save(filename, File(handle), save=False)
            image.save()
        return image
