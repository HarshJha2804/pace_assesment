import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "pace_project.users"
    verbose_name = _("Users")

    def ready(self):
        import pace_project.users.signals
        with contextlib.suppress(ImportError):
            import pace_project.users.signals  # noqa: F401
