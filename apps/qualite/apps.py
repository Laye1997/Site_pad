from django.apps import AppConfig


class QualiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.qualite"
    verbose_name = "Qualité & certifications"

    def ready(self):
        from apps.qualite import pages  # noqa: F401
