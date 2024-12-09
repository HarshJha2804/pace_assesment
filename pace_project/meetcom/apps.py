import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MeetcomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "pace_project.meetcom"
    verbose_name = _("MeetCom")

    def ready(self):
        import pace_project.meetcom.signals
        with contextlib.suppress(ImportError):
            import pace_project.meetcom.signals  # noqa: F401
