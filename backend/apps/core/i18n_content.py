"""Traduction du contenu éditorial (StreamField) vers une autre langue.

Politique déclarative : pour chaque type de bloc de `apps.core.blocks` et
`apps.cms.home_blocks`, on indique quelles clés contiennent du texte à
traduire (TEXT), du texte enrichi HTML (RICHTEXT), une liste (LIST) ou un
sous-bloc (DICT), et lesquelles ne doivent jamais être touchées (identifiants
d'image, URL, noms propres...). Utilisé par `seed_translations` : ne dépend
que de dictionnaires/chaînes (le format JSON brut d'un StreamField), pas des
classes de bloc elles-mêmes, pour rester simple et testable.
"""

from __future__ import annotations

import re
from typing import Any

TEXT = "text"
RICHTEXT = "richtext"

# type de bloc -> { clé: règle }. Une règle est TEXT, RICHTEXT, ("list", règle)
# ou un dict de politique (bloc imbriqué). Toute clé absente de la politique
# n'est pas traduite (image, url, id, valeur numérique, nom propre...).
BLOCK_POLICIES: dict[str, Any] = {
    "heading": {"text": TEXT},
    "paragraph": RICHTEXT,  # RichTextBlock : la valeur du bloc EST le texte
    "image": {"caption": TEXT, "alt": TEXT},
    "gallery": {"title": TEXT, "images": ("list", {"caption": TEXT, "alt": TEXT})},
    "callout": {"title": TEXT, "body": TEXT},
    "cta": {"label": TEXT},
    "table": {"headers": ("list", TEXT), "rows": ("list", ("list", TEXT))},
    "org_chart": {"groups": ("list", {"title": TEXT, "members": ("list", {"role": TEXT})})},
    "org_structure": {
        "governance_title": TEXT,
        "governance_branches": ("list", TEXT),
        "dg_title": TEXT,
        "dg_attached": ("list", TEXT),
        "dg_cells": ("list", TEXT),
        "secretariat_title": TEXT,
        "secretariat_cells": ("list", TEXT),
        "directions": ("list", {"title": TEXT, "departments": ("list", TEXT)}),
        "regional_title": TEXT,
    },
    # Sections de l'accueil (apps.cms.home_blocks)
    "hero": {"eyebrow": TEXT, "title": TEXT, "intro": TEXT},
    "sponsoring": {"eyebrow": TEXT, "title": TEXT, "text": TEXT},
    "president_vision": {
        "eyebrow": TEXT,
        "title": TEXT,
        "intro": RICHTEXT,
        "pillars": ("list", {"title": TEXT, "text": TEXT}),
        "quote": TEXT,
        "quote_author": TEXT,
        "image_alt": TEXT,
    },
    "director_word": {"eyebrow": TEXT, "title": TEXT, "body": RICHTEXT, "image_alt": TEXT},
    "news": {"title": TEXT, "all_link_label": TEXT},
    "service_band": {
        "services_title": TEXT,
        "services": ("list", {"label": TEXT}),
        "movement_title": TEXT,
        "movement_links": ("list", {"label": TEXT}),
    },
    "key_figures": {"title": TEXT, "figures": ("list", {"label": TEXT, "source": TEXT})},
    "hub": {"title": TEXT, "text": TEXT, "image_alt": TEXT, "button_label": TEXT},
    "pro_band": {"title": TEXT, "lead": TEXT, "button_label": TEXT},
    "notices": {"figures_title": TEXT, "figures_alt": TEXT, "title": TEXT},
    "business": {"title": TEXT, "side_title": TEXT, "side_text": TEXT},
    "join": {"title": TEXT, "items": ("list", {"label": TEXT})},
    "partners_certs": {"partners_title": TEXT, "certs_title": TEXT},
    "explore": {"eyebrow": TEXT, "title": TEXT},
    "audiences": {
        "eyebrow": TEXT,
        "title": TEXT,
        "intro": TEXT,
        "items": ("list", {"title": TEXT, "text": TEXT}),
    },
    # StreamField apart, non listée dans ContentStreamBlock : HomePage.key_figures
    "figure": {"label": TEXT, "source": TEXT},
}

_TAG_RE = re.compile(r"(<[^>]+>)")


def _walk_texts(value: Any, rule: Any, out: list[str]) -> None:
    if rule is TEXT:
        if isinstance(value, str) and value.strip():
            out.append(value)
    elif rule is RICHTEXT:
        if isinstance(value, str) and value.strip():
            for piece in _TAG_RE.split(value):
                if piece and not piece.startswith("<") and piece.strip():
                    out.append(piece)
    elif isinstance(rule, tuple) and rule[0] == "list":
        item_rule = rule[1]
        for entry in value or []:
            # Wagtail ListBlock : chaque élément est {"type": "item", "value": ..., "id": ...},
            # pas la valeur elle-même — il faut déballer avant de récurser.
            inner = entry["value"] if isinstance(entry, dict) and "value" in entry else entry
            _walk_texts(inner, item_rule, out)
    elif isinstance(rule, dict):
        value = value or {}
        for key, sub_rule in rule.items():
            if key in value:
                _walk_texts(value[key], sub_rule, out)


def _apply_texts(value: Any, rule: Any, translations: dict[str, str]) -> Any:
    if rule is TEXT:
        if isinstance(value, str) and value.strip():
            return translations.get(value, value)
        return value
    if rule is RICHTEXT:
        if isinstance(value, str) and value.strip():
            return "".join(
                translations.get(piece, piece) if not piece.startswith("<") else piece
                for piece in _TAG_RE.split(value)
            )
        return value
    if isinstance(rule, tuple) and rule[0] == "list":
        item_rule = rule[1]
        result = []
        for entry in value or []:
            if isinstance(entry, dict) and "value" in entry:
                new_entry = dict(entry)
                new_entry["value"] = _apply_texts(entry["value"], item_rule, translations)
                result.append(new_entry)
            else:
                result.append(_apply_texts(entry, item_rule, translations))
        return result
    if isinstance(rule, dict):
        value = dict(value or {})
        for key, sub_rule in rule.items():
            if key in value:
                value[key] = _apply_texts(value[key], sub_rule, translations)
        return value
    return value


def collect_streamfield_texts(
    raw_stream: list[dict[str, Any]], out: list[str] | None = None
) -> list[str]:
    """Chaînes traduisibles d'un StreamField (format brut : liste de {type, value})."""
    out = [] if out is None else out
    for block in raw_stream or []:
        policy = BLOCK_POLICIES.get(block.get("type", ""))
        if policy is not None:
            _walk_texts(block.get("value"), policy, out)
    return out


def translate_streamfield_texts(
    raw_stream: list[dict[str, Any]], translations: dict[str, str]
) -> list[dict[str, Any]]:
    """Nouvelle liste de blocs avec les chaînes traduites (structure/ids inchangés)."""
    result = []
    for block in raw_stream or []:
        policy = BLOCK_POLICIES.get(block.get("type", ""))
        new_block = dict(block)
        if policy is not None:
            new_block["value"] = _apply_texts(block.get("value"), policy, translations)
        result.append(new_block)
    return result
