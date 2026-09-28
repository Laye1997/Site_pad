"""Client minimal de l'API OpenAI (Chat Completions, en streaming), sans dépendance externe.

Compatible avec toute API « OpenAI-like » via ASSISTANT["BASE_URL"] (Azure OpenAI, Mistral…).
"""

import json
import logging
import re
import urllib.error
import urllib.request
from collections.abc import Iterator

from django.conf import settings

logger = logging.getLogger(__name__)

# Les modèles « raisonnement » (o1, o3, gpt-5…) refusent une température personnalisée.
REASONING_MODEL = re.compile(r"^(o\d|gpt-5)")


class LLMError(Exception):
    """Le fournisseur d'IA est injoignable ou a refusé la requête."""

    def __init__(self, message: str, status: int = 503):
        super().__init__(message)
        self.status = status


def open_stream(messages: list[dict]) -> Iterator[str]:
    """Ouvre la connexion (les erreurs remontent ICI, avant toute réponse au navigateur),
    puis renvoie un itérateur sur les morceaux de texte générés."""
    conf = settings.ASSISTANT
    if not conf["API_KEY"]:
        raise LLMError("OPENAI_API_KEY non configurée", status=503)
    url = conf["BASE_URL"].rstrip("/") + "/chat/completions"
    if not url.startswith(("https://", "http://")):
        raise LLMError("ASSISTANT_BASE_URL invalide", status=503)

    payload = {
        "model": conf["MODEL"],
        "messages": messages,
        "stream": True,
        "max_completion_tokens": conf["MAX_TOKENS"],
    }
    if not REASONING_MODEL.match(conf["MODEL"]):
        payload["temperature"] = 0.2

    request = urllib.request.Request(  # noqa: S310 — URL issue des réglages, schéma vérifié
        url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {conf['API_KEY']}",
        },
    )
    try:
        response = urllib.request.urlopen(request, timeout=conf["TIMEOUT"])  # noqa: S310
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:500].decode("utf-8", "ignore")
        logger.error("Assistant : erreur fournisseur %s — %s", exc.code, detail)
        raise LLMError(
            "Erreur du fournisseur d'IA", status=429 if exc.code == 429 else 502
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.error("Assistant : fournisseur injoignable — %s", exc)
        raise LLMError("Fournisseur d'IA injoignable") from exc

    return _iter_tokens(response)


def _iter_tokens(response) -> Iterator[str]:
    """Lit le flux SSE (« data: {...} ») et produit le texte au fil de l'eau."""
    try:
        for raw in response:
            line = raw.decode("utf-8", "ignore").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                delta = json.loads(data)["choices"][0]["delta"].get("content")
            except (ValueError, KeyError, IndexError):
                continue
            if delta:
                yield delta
    except (OSError, TimeoutError) as exc:
        logger.warning("Assistant : flux interrompu — %s", exc)
    finally:
        response.close()
