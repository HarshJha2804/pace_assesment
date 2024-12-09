from notifications.signals import notify

from pace_project.core.models.application_models import Application
from pace_project.users.middlewares import get_current_request
from pace_project.users.models import ApplicationManager


def notify_application_manager(*, application: Application):
    request = get_current_request()
    application_manager_head = ApplicationManager.objects.filter(
        employee__assigned_universities=application.course.university, is_head=True, employee__user__is_active=True
    ).first()
    if application_manager_head and request.user:
        verb = f"Partner {application.student.partner} has direct apply for {application.student}!"
        notify.send(
            sender=request.user,
            recipient=application_manager_head.employee.user,
            verb=verb,
            action_object=application,
            target=application.student,
        )
