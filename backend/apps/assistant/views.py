"""Point d'entrée HTTP de l'assistant : POST JSON → réponse texte en streaming.

Sécurité (cf. ADR 0004) :
- fonction pilotée par feature flag (FEATURE_ASSISTANT) ;
- même origine obligatoire (en-tête Origin/Referer) : widget utilisable depuis le site seul ;
- quotas par IP et quota global journalier (maîtrise des coûts) ;
- aucun message d'utilisateur n'est journalisé.
"""

import json
import logging
from urllib.parse import urlsplit

from django.conf import settings
from django.core.cache import cache
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.assistant import services
from apps.assistant.llm import LLMError

logger = logging.getLogger(__name__)


def _client_ip(request) -> str:
    # Derrière nginx, l'adresse réelle est la dernière ajoutée à X-Forwarded-For.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")


def _same_origin(request) -> bool:
    source = request.META.get("HTTP_ORIGIN") or request.META.get("HTTP_REFERER") or ""
    return bool(source) and urlsplit(source).netloc == request.get_host()


def _over_quota(request) -> bool:
    """Compteurs en cache (Redis en production) : par minute, par jour et global."""
    conf = settings.ASSISTANT
    ip = _client_ip(request)
    now = timezone.now()
    counters = [
        (f"assistant:m:{ip}:{now:%Y%m%d%H%M}", 60, conf["RATE_PER_MINUTE"]),
        (f"assistant:d:{ip}:{now:%Y%m%d}", 86_400, conf["RATE_PER_DAY"]),
        (f"assistant:g:{now:%Y%m%d}", 86_400, conf["GLOBAL_PER_DAY"]),
    ]
    for key, ttl, limit in counters:
        cache.add(key, 0, ttl)
        try:
            count = cache.incr(key)
        except ValueError:  # clé expirée entre-temps
            cache.set(key, 1, ttl)
            count = 1
        if count > limit:
            return True
    return False


def _error(message: str, status: int) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


# Pas de jeton CSRF : aucune session ni donnée modifiée ; la vérification d'origine ci-dessous
# empêche l'usage depuis un autre site, et les quotas limitent les abus.
@csrf_exempt
@require_POST
def chat(request):
    if not settings.FEATURES["assistant"]:
        raise Http404
    if not _same_origin(request):
        return _error(_("Requête non autorisée."), 403)
    if len(request.body) > 32_000:
        return _error(_("Message trop long."), 413)
    try:
        payload = json.loads(request.body)
    except ValueError:
        return _error(_("Requête invalide."), 400)
    if _over_quota(request):
        return _error(
            _("Vous avez envoyé beaucoup de questions. Merci de réessayer dans quelques minutes."),
            429,
        )

    language = payload.get("language") or get_language() or settings.LANGUAGE_CODE
    language = language if language in dict(settings.LANGUAGES) else settings.LANGUAGE_CODE
    try:
        answer = services.prepare_answer(payload.get("messages"), language)
    except ValueError:
        return _error(_("Requête invalide."), 400)
    except LLMError as exc:
        return _error(_("L'assistant est momentanément indisponible."), exc.status)

    response = StreamingHttpResponse(answer.stream, content_type="text/plain; charset=utf-8")
    response["Cache-Control"] = "no-store"
    response["X-Accel-Buffering"] = "no"  # nginx transmet chaque morceau sans attendre la fin
    response["X-Assistant-Sources"] = json.dumps(answer.sources)  # ASCII (échappement \u)
    return response
