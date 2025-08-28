from django.apps import AppConfig

class SocialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "social"

    def ready(self):
        import social.signals  # noqa: F401  <-- absolute import to avoid squiggles
        # or: from . import signals  # noqa: F401
