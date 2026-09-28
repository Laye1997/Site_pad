from django.apps import AppConfig


class AssistantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.assistant"
    verbose_name = "Assistant virtuel"

    def ready(self):
        from wagtail.signals import page_published, page_unpublished

        from apps.assistant.index import invalidate

        # Une page publiée ou dépubliée : l'assistant relit le site à la prochaine question.
        page_published.connect(invalidate, dispatch_uid="assistant_invalidate_published")
        page_unpublished.connect(invalidate, dispatch_uid="assistant_invalidate_unpublished")
