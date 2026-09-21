"""Application Celery : tâches de fond (e-mails, alertes, imports)."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("pad")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
