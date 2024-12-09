import contextlib

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pace_project.core'

    def ready(self):
        import pace_project.users.signals
        with contextlib.suppress(ImportError):
            import pace_project.core.signals  # noqa: F401
