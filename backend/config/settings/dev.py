"""Réglages de développement local."""

from .base import *  # noqa: F401,F403

DEBUG = True
SECRET_KEY = "dev-insecure-key-change-me"  # noqa: S105
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Barre de débogage optionnelle si installée.
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass
