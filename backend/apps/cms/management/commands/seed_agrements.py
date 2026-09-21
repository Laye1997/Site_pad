"""Développe « Procédures et agréments » : obtenir, renouveler, formulaires de chiffres d'affaires.

Contenu et PDF repris de l'ancien site (rubrique Opportunités d'affaires > Agréments). Les PDF sont
importés comme documents Wagtail téléchargeables. Idempotent ; --force réécrit le texte des pages.
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.documents.models import Document
from wagtail.models import Page, Site

from apps.cms.models import StandardPage
from apps.core.blocks import ContentStreamBlock

DOCS_DIR = Path(settings.BASE_DIR) / "data" / "documents" / "agrements"
PORTAL_URL = "https://atlantis.portdakar.sn"
SIGNUP_URL = "https://atlantis.portdakar.sn/creationcompte.padpublic?userParam=ADD"
PARENT_SLUG = "procedures-agrements"

# (intitulé, fichier PDF)
OBTENIR = [
    ("Profession de transitaire", "liste_des_pieces_a_fournir_pour_lagrement_transitaire_2025.pdf"),
    ("Profession de transporteur de conteneurs", "nvlle_demande_transport_2025.pdf"),
    (
        "Profession de manutentionnaire",
        "liste_des_pieces_a_fournir_pour_lagrement_manutentionnaire_2025.pdf",
    ),
    (
        "Profession de consignataire",
        "liste_des_pieces_a_fournir_pour_lagrement_consignataire_2025_0.pdf",
    ),
    (
        "Autorisation d'exercer à bord des navires",
        "liste_des_pieces_a_fournir_pour_autorisation_2025.pdf",
    ),
    (
        "Profession de shipchandler",
        "liste_des_pieces_a_fournir_pour_lagrement_shipchandler_2025.pdf",
    ),
    ("Activité de remorquage", "liste_des_pieces_a_fournir_pour_lagrement_remorquage_2025.pdf"),
]
RENOUVELER = [
    (
        "Renouvellement de l'agrément de transport de conteneurs",
        "renouvellement_transport2025.pdf",
    ),
]
FORMULAIRES = [
    ("Transport de conteneurs", "formulaire_declaration_ca_transporteur_de_conteneurs.pdf"),
    ("Transit", "formulaire_declaration_ca_transitaire.pdf"),
    ("Shipchandling", "formulaire_declaration_ca_shipchandler_0.pdf"),
    ("Consignation", "formulaire_declaration_ca_consignataire.pdf"),
    ("Manutention", "formulaire_declaration_ca_manutentionnaire.pdf"),
]

PAGES = [
    ("Obtenir un agrément", "obtenir-un-agrement"),
    ("Renouveler son agrément", "renouveler-son-agrement"),
    (
        "Formulaires de déclaration de chiffres d'affaires",
        "formulaires-declaration-chiffres-affaires",
    ),
]


def _document(filename: str, title: str):
    existing = Document.objects.filter(title=title).first()
    if existing:
        return existing
    path = DOCS_DIR / filename
    if not path.exists():
        return None
    with path.open("rb") as handle:
        document = Document(title=title)
        document.file.save(filename, File(handle), save=False)
        document.save()
    return document


def _size(document) -> str:
    kilobytes = document.file.size / 1024
    return f"{kilobytes / 1024:.1f} Mo" if kilobytes >= 1024 else f"{kilobytes:.0f} Ko"


def _link(document, label: str) -> str:
    if document is None:
        return f"{label} (document indisponible)"
    return f'<a id="{document.pk}" linktype="document">{label}</a> ' f"(PDF, {_size(document)})"


def _p(html):
    return {"type": "paragraph", "value": f"<p>{html}</p>"}


def _h(text):
    return {"type": "heading", "value": {"text": text, "level": "h2"}}


def _cta(label, url):
    return {"type": "cta", "value": {"label": label, "url": url}}


def _contact():
    return {
        "type": "callout",
        "value": {
            "title": "Une question sur votre dossier ?",
            "body": "Numéro vert du Port Autonome de Dakar : 800 801 802.",
        },
    }


def _portal():
    return [
        _h("Espace Pro"),
        _p("Les démarches en ligne se font depuis le portail de service."),
        _cta("Se connecter au portail", PORTAL_URL),
        _cta("Créer un compte", SIGNUP_URL),
    ]


def _documents_block(items):
    return [
        block
        for title, filename in items
        for block in (
            _h(title),
            _p(_link(_document(filename, title), "Liste des pièces à fournir")),
        )
    ]


def obtenir():
    return [
        _p(
            "Pour exercer une profession ou une activité au port, consultez ci-dessous la liste "
            "des pièces à fournir correspondant à votre profession."
        ),
        *_documents_block(OBTENIR),
        _contact(),
        *_portal(),
    ]


def renouveler():
    body = [
        _p("Retrouvez ci-dessous la liste des pièces à fournir pour renouveler votre agrément."),
    ]
    for title, filename in RENOUVELER:
        body += [_h(title), _p(_link(_document(filename, title), "Liste des pièces à fournir"))]
    return [*body, _contact(), *_portal()]


def formulaires():
    items = ""
    for title, filename in FORMULAIRES:
        document = _document(filename, f"Formulaire de déclaration de CA — {title}")
        items += f"<li>{_link(document, title)}</li>"
    return [
        _p(
            "Les agréés déclarent leur chiffre d'affaires à l'aide du formulaire correspondant à "
            "leur profession :"
        ),
        {"type": "paragraph", "value": f"<ul>{items}</ul>"},
        _contact(),
    ]


INDEX_BODY = [
    _p(
        "Cette rubrique regroupe les démarches d'agrément au Port Autonome de Dakar : obtenir "
        "un agrément, le renouveler, et déclarer son chiffre d'affaires. Choisissez une "
        "démarche dans le menu de la rubrique."
    ),
    _contact(),
]

BUILDERS = {
    "obtenir-un-agrement": obtenir,
    "renouveler-son-agrement": renouveler,
    "formulaires-declaration-chiffres-affaires": formulaires,
}


class Command(BaseCommand):
    help = "Développe les pages d'agrément (Procédures et agréments) avec les PDF de l'ancien site."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le texte des pages.")

    def handle(self, *args, force: bool, **options):
        root = Site.objects.get(is_default_site=True).root_page
        parent = Page.objects.descendant_of(root).filter(slug=PARENT_SLUG).first()
        if parent is None:
            self.stdout.write(
                "Page « Procédures et agréments » introuvable : lancez seed_site_structure."
            )
            return
        parent = parent.specific
        if force or not len(parent.body):
            parent.body = ContentStreamBlock().to_python(INDEX_BODY)
            parent.save_revision().publish()
            self.stdout.write("Procédures et agréments : introduction enregistrée.")
        for title, slug in PAGES:
            page = parent.get_children().filter(slug=slug).first()
            if page is None:
                page = StandardPage(title=title, slug=slug, show_in_menus=True)
                parent.add_child(instance=page)
                page = page.specific
                created = True
            else:
                page = page.specific
                created = False
            if created or force or not len(page.body):
                page.body = ContentStreamBlock().to_python(BUILDERS[slug]())
                page.save_revision().publish()
                self.stdout.write(f"{title} : {'créée' if created else 'mise à jour'}.")
            else:
                self.stdout.write(f"{title} : contenu déjà présent, ignoré.")
