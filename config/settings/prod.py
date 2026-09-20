"""Réglages de production — durcis (ISO 27001 / bonnes pratiques Django)."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE, SECRET_KEY, STORAGES, env

DEBUG = False

# Refus de démarrer avec une clé de développement ou d'exemple (aucun secret par défaut en prod).
if SECRET_KEY.startswith("dev-insecure") or "change-me" in SECRET_KEY or len(SECRET_KEY) < 32:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY doit être définie avec une valeur secrète d'au moins 32 caractères."
    )

# HTTPS / cookies sécurisés
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Content-Security-Policy (django-csp). Aucun script ni style inline sur le site public :
# les scripts vivent dans static/js/. L'admin Wagtail, qui en utilise, est exclu de la politique.
MIDDLEWARE.insert(1, "csp.middleware.CSPMiddleware")
CONTENT_SECURITY_POLICY = {
    "EXCLUDE_URL_PREFIXES": ["/admin/", "/django-admin/"],
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "media-src": ["'self'"],
        "font-src": ["'self'"],
        "style-src": ["'self'"],
        "script-src": ["'self'"],
        "connect-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'none'"],
    },
}

# Journalisation vers la sortie standard (récupérée par l'orchestrateur).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# Suivi d'erreurs : actif seulement si SENTRY_DSN est défini (aucune donnée personnelle envoyée).
if env("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        environment=env("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=float(env("SENTRY_TRACES_SAMPLE_RATE", "0.05")),
        send_default_pii=False,
    )

# Le mode manifest (hash des fichiers) est réservé à la prod pour éviter les erreurs
# de templates Django/Wagtail en environnement de développement.
STORAGES["staticfiles"] = {  # type: ignore[index]
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}
