from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PartnerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pace_project.partner'
    verbose_name = _("Partners")

    def ready(self):
        import pace_project.partner.signals


