from django.db.models.signals import post_save
from django.dispatch import receiver

from pace_project.core.models.application_models import Application
from pace_project.core.notifications import notify_application_manager_on_assignment
from pace_project.core.services import assign_application_manager


@receiver(post_save, sender=Application)
def signal_assign_application(sender, instance, created, **kwargs):
    if created:
        next_manager = assign_application_manager(application=instance)
        if next_manager:
            notify_application_manager_on_assignment(application=instance, app_manager=next_manager)
