from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import StatusType
from pace_project.paceapp.models import Course, Intake, Year
from pace_project.users.middlewares import get_current_request
from pace_project.users.models import Student


def is_valid_application_parameters(*, course_id: int, intake_id: int, year_id: int) -> bool:
    """Check if the provided course, intake, and year IDs exist."""
    return (
        Course.objects.filter(id=course_id).exists() and
        Intake.objects.filter(id=intake_id).exists() and
        Year.objects.filter(id=year_id).exists()
    )


def is_application_already_applied(*, student: Student, course_id: int, intake_id: int, year_id: int) -> bool:
    return Application.objects.filter(
        student=student,
        course_id=course_id,
        intake_id=intake_id, year_id=year_id
    ).exists()


def create_application(*, student: Student, status: StatusType, course_id: int, intake_id: int,
                       year_id: int) -> Application:
    """Create an application for a student with specified course, intake, and year IDs."""
    logged_in_user = get_current_request().user
    return Application.objects.create(
        student=student,
        course_id=course_id,
        intake_id=intake_id,
        year_id=year_id,
        current_status=status,
        created_by=logged_in_user
    )


def sent_mail_to_university_on_ass_request(*, ass_requests):
    for ass_request in ass_requests:
        if not ass_request.university.email:
            continue
        context = {'object': ass_request}
        subject = f"Assessment request from  {ass_request.student.partner} for {ass_request.student}!"
        email_message = render_to_string("emailtemplates/assessment/assessment_request_university.html", context)
        send_mail(
            subject,
            email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ass_request.university.email],
            fail_silently=False,
            html_message=email_message
        )


