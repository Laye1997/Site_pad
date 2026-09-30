"""Crée la locale anglaise et publie la traduction du contenu éditorial existant.

Le contenu des pages (titres, textes, organigramme…) n'existe qu'en français : Wagtail affiche
la page française sous /en/ faute d'équivalent anglais. Cette commande crée, pour chaque page
française publiée, une copie dans la locale anglaise puis traduit ses champs texte et StreamField
à l'aide du dictionnaire `backend/data/i18n/fr_en.json` (généré une fois, à partir du contenu
existant — toute nouvelle phrase ajoutée en français devra être ajoutée à ce dictionnaire).
Idempotent : ignore les pages déjà traduites et publiées en anglais, sauf --force.
"""

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from wagtail.models import Locale, Page

from apps.core.i18n_content import collect_streamfield_texts, translate_streamfield_texts

SIMPLE_FIELDS = ["title", "seo_title", "search_description", "share_image_alt"]
MODEL_EXTRA_SIMPLE = {
    "homepage": ["hero_title", "intro"],
    "mediaindexpage": ["intro"],
    "serviceindexpage": ["intro"],
    "pageqse": ["intro"],
    "recruitmentindexpage": ["intro"],
    "articlepage": ["summary", "cover_alt"],
    "servicepage": ["summary", "illustration_alt"],
}
STREAMFIELD_NAMES: dict[str, list[str]] = {
    "homepage": ["key_figures", "sections", "body"],
    "standardpage": ["body"],
    "articlepage": ["body"],
    "servicepage": ["body"],
    "pageqse": ["body"],
    "recruitmentindexpage": ["body"],
}


def load_translations() -> dict[str, str]:
    path = Path(settings.BASE_DIR) / "data" / "i18n" / "fr_en.json"
    return json.loads(path.read_text(encoding="utf-8"))


def translate_value(value: str, translations: dict[str, str], missing: list[str]) -> str:
    if not value.strip():
        return value
    if value in translations:
        return translations[value]
    missing.append(value)
    return value


class Command(BaseCommand):
    help = "Crée la locale anglaise et traduit le contenu des pages existantes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Retraduit même les pages déjà publiées en anglais.",
        )

    def handle(self, *args: Any, force: bool, **options: Any):
        translations = load_translations()
        fr_locale = Locale.objects.get(language_code="fr")
        en_locale, created = Locale.objects.get_or_create(language_code="en")
        if created:
            self.stdout.write("Locale en créée.")

        missing: list[str] = []
        made, updated, skipped = 0, 0, 0

        for page in Page.objects.filter(locale=fr_locale, depth__gt=1).order_by("depth", "path"):
            fr_specific = page.specific
            model = fr_specific._meta.model_name

            en_page = fr_specific.get_translation_or_none(en_locale)
            if en_page is None:
                en_page = fr_specific.copy_for_translation(en_locale, copy_parents=True)
                made += 1
            elif en_page.specific.live and not force:
                skipped += 1
                continue
            else:
                updated += 1

            en_specific = en_page.specific

            for field in SIMPLE_FIELDS + MODEL_EXTRA_SIMPLE.get(model, []):
                value = getattr(fr_specific, field, "") or ""
                setattr(en_specific, field, translate_value(value, translations, missing))

            for field in STREAMFIELD_NAMES.get(model, []):
                fr_stream = getattr(fr_specific, field, None)
                if fr_stream is None:
                    continue
                raw = fr_stream.raw_data
                found = collect_streamfield_texts(raw)
                missing.extend(text for text in found if text not in translations)
                translated_raw = translate_streamfield_texts(raw, translations)
                stream_block = type(en_specific)._meta.get_field(field).stream_block
                setattr(en_specific, field, stream_block.to_python(translated_raw))

            en_specific.save_revision().publish()

        self.stdout.write(
            f"Pages traduites : {made} créées, {updated} mises à jour, {skipped} ignorées."
        )
        if missing:
            unique_missing = sorted(set(missing))
            self.stdout.write(
                self.style.WARNING(
                    f"{len(unique_missing)} chaîne(s) sans traduction (laissées en français) : "
                    + "; ".join(unique_missing[:10])
                    + (" …" if len(unique_missing) > 10 else "")
                )
            )
