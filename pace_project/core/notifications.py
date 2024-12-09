from pace_project.core.models.application_models import Application
from notifications.signals import notify

from pace_project.users.middlewares import get_current_request
from pace_project.users.models import Employee
from django.contrib.auth import get_user_model

User = get_user_model()


def notify_application_manager_on_assignment(*, application: Application, app_manager: Employee):
    """Notify application manager on new application assignment."""
    request = get_current_request()
    logged_in_user = request.user
    verb_msb = f"New application assignment of {application.course.university}"
    notify.send(logged_in_user, recipient=app_manager.user, verb=verb_msb, action_object=application)


def notify_partner_on_status_change(*, application: Application, sender: User):
    """Notify partner on application status change."""
    if application.student.partner.user:
        recipient = application.student.partner.user
        verb_msg = f"New update on the status of application for student: {application.student}!"
        notify.send(sender, recipient=recipient, verb=verb_msg, action_object=application, )
