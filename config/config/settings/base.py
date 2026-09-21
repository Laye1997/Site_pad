"""
Réglages communs à tous les environnements.

Les valeurs sensibles ou dépendantes de l'environnement sont lues depuis
des variables d'environnement (12-factor) — jamais codées en dur.
"""

import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def env_bool(key: str, default: bool = False) -> bool:
    return env(key, str(default)).lower() in {"1", "true", "yes", "on"}


# --- Sécurité de base (surchargée en prod) ---------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = [h for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]

# --- Applications -----------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.sitemaps",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
]

# Apps métier du projet — un module par domaine fonctionnel (bounded context).
LOCAL_APPS = [
    "apps.core",
    "apps.cms",
    "apps.services",
    "apps.media",
    "apps.navires",
    "apps.marches",
    "apps.espace_pro",
    "apps.recrutement",
    "apps.qualite",
    "apps.api",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "axes",  # limitation des tentatives de connexion (ISO 27001 — contrôle d'accès)
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # i18n FR/EN
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "wagtail.contrib.settings.context_processors.settings",
                "apps.core.context_processors.site_navigation",
                "apps.core.context_processors.features",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Base de données --------------------------------------------------------
# PostgreSQL en prod (via DATABASE_URL) ; SQLite par défaut pour démarrer vite.
DATABASES: dict[str, dict[str, Any]]
if env("DATABASE_URL"):
    import dj_database_url

    DATABASES = {"default": dict(dj_database_url.parse(env("DATABASE_URL"), conn_max_age=600))}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Cache & tâches asynchrones ---------------------------------------------
# Redis si REDIS_URL est défini ; sinon cache local et tâches exécutées sur place.
REDIS_URL = env("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
    CELERY_BROKER_URL = REDIS_URL
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    CELERY_BROKER_URL = "memory://"
CELERY_TASK_ALWAYS_EAGER = not REDIS_URL
CELERY_TIMEZONE = "Africa/Dakar"
CELERY_BEAT_SCHEDULE = {
    "alerte-expiration-certifications": {
        "task": "apps.qualite.tasks.alert_expiring_certifications",
        "schedule": 60 * 60 * 24,
    },
}
CERTIFICATION_ALERT_DAYS = 90
CERTIFICATION_ALERT_EMAILS = [e for e in env("CERTIFICATION_ALERT_EMAILS", "").split(",") if e]

# --- Feature flags ----------------------------------------------------------
FEATURES = {
    "consent_banner": env_bool("FEATURE_CONSENT_BANNER", True),
    "public_api": env_bool("FEATURE_PUBLIC_API", True),
    "home_ship_movement": env_bool("FEATURE_HOME_SHIP_MOVEMENT", True),
}

# Réseaux sociaux : renseigner les URL officielles par variable d'environnement (masqués si vides).
SOCIAL_LINKS = {
    "Facebook": env("SOCIAL_FACEBOOK_URL"),
    "X": env("SOCIAL_X_URL"),
    "Instagram": env("SOCIAL_INSTAGRAM_URL"),
    "YouTube": env("SOCIAL_YOUTUBE_URL"),
    "LinkedIn": env("SOCIAL_LINKEDIN_URL"),
}

# --- API (DRF) ---------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "120/min"},
    "UNAUTHENTICATED_USER": None,
}

# --- Protection contre la force brute (django-axes) ---------------------------
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # heures
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]

# --- Mots de passe ----------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation (multilingue FR / EN) -----------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Dakar"
USE_I18N = True
USE_TZ = True
LANGUAGES = [("fr", "Français"), ("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES

# --- Fichiers statiques & médias -------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "espace_pro:login"
LOGIN_REDIRECT_URL = "espace_pro:dashboard"
LOGOUT_REDIRECT_URL = "espace_pro:login"

# --- Wagtail ---------------------------------------------------------------
WAGTAIL_SITE_NAME = "Port Autonome de Dakar"
WAGTAILADMIN_BASE_URL = env("WAGTAILADMIN_BASE_URL", "http://localhost:8000")
WAGTAILIMAGES_FORMAT_CONVERSIONS = {"png": "webp", "jpeg": "webp"}
WAGTAILDOCS_EXTENSIONS = ["pdf", "docx", "xlsx", "csv", "odt", "ods"]
RECRUITMENT_EMAIL = env("RECRUITMENT_EMAIL", "rh@portdakar.sn")
APPLICATION_MAX_UPLOAD_SIZE = 5 * 1024 * 1024

# --- En-têtes de sécurité (renforcés en prod) -------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
