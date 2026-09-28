"""Index de recherche de l'assistant : les pages publiées du site + la FAQ éditoriale.

Le contenu des pages Wagtail est découpé en passages courts, indexés en mémoire (BM25).
Aucune base vectorielle ni service tiers : l'index se reconstruit en quelques millisecondes
et est invalidé à chaque publication de page (signal branché dans apps.py).
"""

import math
import re
import time
import unicodedata
from dataclasses import dataclass, field

from django.conf import settings
from django.core.cache import cache
from django.utils.html import strip_tags

VERSION_KEY = "assistant:index-version"
INDEX_TTL = 600  # secondes : filet de sécurité si un signal de publication est manqué
PASSAGE_CHARS = 700

# Mots vides FR/EN retirés des requêtes et des passages.
STOPWORDS = set("""
    les des une un le la de du et ou en au aux a pour par sur dans est sont que qui quoi quel
    quelle quels quelles comment combien ce cet cette ces il elle ils elles on nous vous je tu me
    te se mon ma mes ton ta tes son sa ses leur leurs avec sans pas plus peut peux puis faire fait
    etre avoir y ne donne donner dire savoir voudrais veux svp merci bonjour pad port dakar autonome
    the of and to is are what how can do does in on for with a an my your me i you please about
    """.split())
# « port », « dakar », « pad » apparaissent partout : ils ne départagent aucun passage.

# Le contenu est en français : quelques équivalents anglais pour les questions posées en anglais.
EN_FR = {
    "ship": "navire", "ships": "navire", "vessel": "navire", "vessels": "navire", "boat": "bateau",
    "hours": "horaires", "opening": "horaires", "schedule": "horaires", "timetable": "horaires",
    "contact": "contacts", "phone": "telephone", "address": "adresse", "email": "mail",
    "pilot": "pilotage", "piloting": "pilotage", "towage": "remorquage", "tug": "remorquage",
    "mooring": "lamanage", "bunkering": "avitaillement", "supply": "avitaillement",
    "repair": "reparation", "cargo": "marchandises", "goods": "marchandises",
    "handling": "manutention", "storage": "stockage", "warehouse": "entreposage",
    "passenger": "passagers", "passengers": "passagers", "ferry": "chaloupe",
    "berth": "quai", "quay": "quai", "cruise": "croisiere", "arrival": "arrivee",
    "departure": "depart", "job": "recrutement", "jobs": "recrutement", "career": "recrutement",
    "careers": "recrutement", "internship": "stage", "apply": "postuler", "tender": "offres",
    "tenders": "offres", "procurement": "marches", "license": "agrement", "approval": "agrement",
    "accreditation": "agrement", "visit": "visite", "history": "historique", "news": "actualites",
    "fees": "tarifs", "prices": "tarifs", "tariff": "tarifs", "security": "surete",
    "safety": "securite", "quality": "qualite", "traffic": "trafic", "figures": "chiffres",
}  # fmt: skip

# Clés de StreamField qui ne contiennent jamais de texte utile.
SKIP_KEYS = {"type", "id", "level", "image", "icon", "style", "variant", "page", "document", "url"}
TODO_MARKERS = ("à compléter", "a completer", "à renseigner")


# Abréviations courantes développées avant la recherche.
ABBREVIATIONS = {
    r"\bdg\b": "directeur général",
    r"\bpca\b": "président du conseil d'administration",
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    for pattern, full in ABBREVIATIONS.items():
        text = re.sub(pattern, full, text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")  # sans accents
    words = re.split(r"[^a-z0-9]+", text)
    tokens = []
    for w in words:
        w = EN_FR.get(w, w)
        if len(w) < 3 or w in STOPWORDS:
            continue
        # Racinisation légère : pluriel retiré puis troncature à 7 lettres.
        # contacter/contacts → « contact », agréments → « agremen », mais directeur (« directe »)
        # reste distinct de direction (« directi »).
        if len(w) > 4 and w[-1] in "sx":
            w = w[:-1]
        tokens.append(w[:7])
    return tokens


@dataclass
class Passage:
    title: str
    text: str
    url: str | None = None
    tf: dict = field(default_factory=dict, repr=False)
    length: int = 0


# ---------------------------------------------------------------------------
# Extraction du texte des pages
# ---------------------------------------------------------------------------
def _stream_strings(value, out: list[str]) -> None:
    """Parcourt la valeur brute d'un StreamField et collecte les textes lisibles."""
    if isinstance(value, str):
        text = " ".join(strip_tags(value).split())
        if len(text) > 2 and not text.startswith(("http://", "https://", "/")):
            out.append(text)
    elif isinstance(value, list):
        for item in value:
            _stream_strings(item, out)
    elif isinstance(value, dict):
        title = str(value.get("title", "")).strip().lower()
        if title in TODO_MARKERS:
            return  # encadrés « À compléter » : notes internes, pas de l'information
        for key, item in value.items():
            if key not in SKIP_KEYS:
                _stream_strings(item, out)


def page_text(page) -> str:
    """Texte brut d'une page Wagtail (champs propres au type de page, hors métadonnées)."""
    from django.db import models
    from wagtail.fields import RichTextField, StreamField
    from wagtail.models import Page

    parts: list[str] = []
    base_fields = {f.name for f in Page._meta.get_fields()}
    for f in type(page)._meta.get_fields():
        if f.name in base_fields or not getattr(f, "concrete", False):
            continue
        if f.name.endswith("_alt") or isinstance(f, models.URLField):
            continue
        value = getattr(page, f.name, None)
        if not value:
            continue
        if isinstance(f, StreamField):
            _stream_strings(value.get_prep_value(), parts)
        elif isinstance(f, RichTextField | models.TextField | models.CharField):
            text = " ".join(strip_tags(str(value)).split())
            if len(text) > 2:
                parts.append(text)
    if page.search_description:
        parts.insert(0, page.search_description)
    kept = [p for p in parts if not any(m in p.lower() for m in TODO_MARKERS)]
    return "\n".join(dict.fromkeys(kept))  # sans doublons, ordre conservé


def _split(text: str, size: int = PASSAGE_CHARS) -> list[str]:
    """Découpe en passages d'environ `size` caractères, sur des fins de phrase."""
    sentences = re.split(r"(?<=[.!?:;])\s+|\n+", text)
    chunks, current = [], ""
    for s in sentences:
        if current and len(current) + len(s) > size:
            chunks.append(current.strip())
            current = ""
        current += " " + s
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _page_passages(language: str) -> list[Passage]:
    from wagtail.models import Locale, Page

    pages = Page.objects.live().public().filter(depth__gt=1)
    locale = Locale.objects.filter(language_code=language).first()
    if locale and pages.filter(locale=locale).exists():
        pages = pages.filter(locale=locale)
    else:  # pas encore de pages traduites : on répond à partir du contenu par défaut
        pages = pages.filter(locale__language_code=settings.LANGUAGE_CODE)

    passages = []
    for page in pages.specific().iterator():
        text = page_text(page)
        if not text:
            continue
        url = page.get_url()
        for chunk in _split(text):
            passages.append(Passage(title=page.title, text=chunk, url=url))
    return passages


# Rubriques servies par des vues Django (pas des pages Wagtail) : décrites ici pour que
# l'assistant puisse y renvoyer. (nom d'URL, titre, description)
APP_SECTIONS = [
    (
        "navires:liste",
        "Mouvement des navires",
        "Liste des escales au port de Dakar : navires attendus, à quai et partis, avec quai, "
        "pavillon, provenance et destination. Suivi du trafic maritime.",
    ),
    (
        "navires:croisieres",
        "Escales de croisière",
        "Calendrier des escales de paquebots de croisière au port de Dakar.",
    ),
    (
        "marches:liste",
        "Marchés publics",
        "Appels d'offres, avis d'attribution et plans de passation des marchés du Port Autonome "
        "de Dakar, filtrables par type et par statut, avec documents à télécharger.",
    ),
    (
        "recrutement:apply",
        "Recrutement — postuler en ligne",
        "Candidature en ligne au Port Autonome de Dakar (emploi, stage, candidature spontanée) : "
        "formulaire avec nom, e-mail, message et CV (PDF ou DOCX, 5 Mo maximum). L'équipe des "
        "ressources humaines revient vers le candidat si son profil correspond.",
    ),
]


def _app_passages(language: str) -> list[Passage]:
    from django.urls import NoReverseMatch, reverse
    from django.utils import translation

    passages = []
    with translation.override(language):
        for name, title, text in APP_SECTIONS:
            try:
                passages.append(Passage(title=title, text=text, url=reverse(name)))
            except NoReverseMatch:
                continue
    return passages


def _faq_passages() -> list[Passage]:
    """FAQ éditoriale (data/assistant/faq.md) : un bloc « ## Titre » = un passage."""
    path = settings.ASSISTANT["FAQ_PATH"]
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    passages = []
    for block in re.split(r"^##\s+", raw, flags=re.M)[1:]:
        title, _, body = block.partition("\n")
        if body.strip():
            passages.append(Passage(title=title.strip(), text=" ".join(body.split())))
    return passages


# ---------------------------------------------------------------------------
# Index BM25 (en mémoire, par langue, partagé entre requêtes du même processus)
# ---------------------------------------------------------------------------
class Index:
    k1, b = 1.4, 0.75

    def __init__(self, passages: list[Passage]):
        self.passages = passages
        self.df: dict[str, int] = {}
        for p in passages:
            # le titre compte double : il résume le passage
            tokens = tokenize(p.title) * 2 + tokenize(p.text)
            p.length = len(tokens)
            for t in tokens:
                p.tf[t] = p.tf.get(t, 0) + 1
            for t in p.tf:
                self.df[t] = self.df.get(t, 0) + 1
        self.avg = sum(p.length for p in passages) / max(len(passages), 1)

    def search(self, query: str, k: int = 5, per_page: int = 2) -> list[Passage]:
        n = len(self.passages)
        terms = set(tokenize(query))
        scored = []
        for p in self.passages:
            score = 0.0
            for t in terms:
                f = p.tf.get(t)
                if not f:
                    continue
                df = self.df[t]
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                score += (
                    idf
                    * f
                    * (self.k1 + 1)
                    / (f + self.k1 * (1 - self.b + self.b * p.length / self.avg))
                )
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)

        results, per_url = [], {}
        for _, p in scored:
            if p.url and per_url.get(p.url, 0) >= per_page:
                continue
            per_url[p.url] = per_url.get(p.url, 0) + 1
            results.append(p)
            if len(results) == k:
                break
        return results


_memo: dict[str, tuple[int, float, Index]] = {}


def get_index(language: str) -> Index:
    version = cache.get_or_set(VERSION_KEY, 1)
    cached = _memo.get(language)
    if cached and cached[0] == version and time.monotonic() - cached[1] < INDEX_TTL:
        return cached[2]
    index = Index(_faq_passages() + _app_passages(language) + _page_passages(language))
    _memo[language] = (version, time.monotonic(), index)
    return index


def invalidate(**kwargs) -> None:
    """Appelé à chaque (dé)publication : tous les processus reconstruiront leur index."""
    try:
        cache.incr(VERSION_KEY)
    except ValueError:
        cache.set(VERSION_KEY, 2)
