"""Service applicatif de l'assistant (interface stable, cf. ADR 0001 et 0004).

`prepare_answer()` cherche les passages utiles, construit la requête au modèle et ouvre le flux.
Le mouvement des navires provient de `apps.navires.services` (jamais de ses modèles).
"""

from collections.abc import Iterator
from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse
from django.utils import translation

from apps.assistant import index, llm, prompts

SHIP_TERMS = {
    "navire", "bateau", "escale", "quai", "arrivee", "depart", "croisiere", "paquebot",
    "mouvement", "ship", "vessel", "cruise", "arrival", "berth",
}  # fmt: skip


@dataclass
class Answer:
    stream: Iterator[str]
    sources: list[dict]


def clean_history(messages) -> list[dict]:
    """Garde les derniers échanges valides, tronqués (le client n'est jamais cru sur parole)."""
    conf = settings.ASSISTANT
    history = []
    for m in messages if isinstance(messages, list) else []:
        if not isinstance(m, dict) or m.get("role") not in {"user", "assistant"}:
            continue
        content = str(m.get("content", "")).strip()
        if content:
            history.append({"role": m["role"], "content": content[: conf["MAX_INPUT_CHARS"]]})
    history = history[-conf["MAX_HISTORY"] :]
    if not history or history[-1]["role"] != "user":
        return []
    return history


def _ship_movement(language: str) -> str:
    """Données en direct sur les escales, ajoutées quand la question porte sur les navires."""
    from apps.navires.services import movement_summary, upcoming_cruises

    summary = movement_summary(limit=8)
    with translation.override(language):
        url = reverse("navires:liste")
    lines = [
        f"### Mouvement des navires — données du jour ({url})",
        f"Navires attendus : {summary['attendus']} ; à quai : {summary['a_quai']} ; "
        f"partis : {summary['partis']}.",
    ]
    for e in summary["prochaines"]:
        quai = f", quai {e.quai}" if e.quai else ""
        lines.append(
            f"- {e.navire} ({e.type_navire}, pavillon {e.pavillon}) : {e.get_statut_display()}, "
            f"arrivée {e.date_arrivee:%d/%m/%Y}{quai}, en provenance de {e.provenance}."
        )
    cruises = upcoming_cruises(limit=5)
    if cruises:
        lines.append("Prochaines escales de croisière :")
        lines += [f"- {c.navire} le {c.date:%d/%m/%Y}" for c in cruises]
    return "\n".join(lines)


def prepare_answer(messages, language: str) -> Answer:
    """Lève `ValueError` si l'historique est invalide, `llm.LLMError` si le modèle est absent."""
    history = clean_history(messages)
    if not history:
        raise ValueError("Le dernier message doit venir de l'utilisateur.")

    # La question courante + la précédente (pour les relances du type « et le numéro ? »).
    user_turns = [m["content"] for m in history if m["role"] == "user"]
    query = " ".join(user_turns[-2:])
    passages = index.get_index(language).search(query, k=settings.ASSISTANT["TOP_K"])
    live = _ship_movement(language) if SHIP_TERMS & set(index.tokenize(query)) else ""

    system = prompts.system_prompt(prompts.format_context(passages, live), language)
    stream = llm.open_stream([{"role": "system", "content": system}, *history])

    sources, seen = [], set()
    for p in passages:
        if p.url and p.url not in seen:
            seen.add(p.url)
            sources.append({"title": p.title, "url": p.url})
    return Answer(stream=stream, sources=sources[:3])
