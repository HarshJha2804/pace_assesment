from django.core.mail import send_mail
from django.template.loader import render_to_string

from pace_project.core.models.application_models import Application, ApplicationRemark
from pace_project.paceapp.models import AssessmentDiscovery
from django.conf import settings


def send_partner_assessment_email(*, assessment: AssessmentDiscovery):
    """
    Sends an email to the partner when a new assessment is received.
    """
    student = assessment.student
    partner_email = student.partner.email

    if not partner_email:
        return

    subject = f"New Assessment Received for {student}"

    # Render the email message using a Django template
    message = render_to_string('emailtemplates/assessment/assessment_received.html', {
        'student': student,
        'assessment': assessment,
    })
    recipient_list = [partner_email]
    if assessment.course.university.email:
        recipient_list.append(assessment.course.university.email)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=message
    )


def send_application_status_update_email(*, application: Application, remark: str):
    """
    Sends an email to the partner notifying them about a status update in the application.
    """
    partner_email = application.student.partner.email

    if not partner_email:
        return

    subject = f"Application Status Update for {application.student}"

    # Render the email message using a Django template
    message = render_to_string('emailtemplates/partner/application_status_update.html', {
        'application': application,
        "remark": remark
    })

    recipient_list = [partner_email]
    if application.course.university.email:
        recipient_list.append(application.course.university.email)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
        html_message=message
    )


def send_partner_application_message_email(*, app_remark: ApplicationRemark):
    """
    Sends an email to the partner when a new message is added to the application.
    """
    partner_email = app_remark.application.student.partner.email

    if not partner_email:
        return

    application = app_remark.application
    subject = f"New Message for {application.student}'s Application"

    # Render the email message using a Django template
    message = render_to_string('emailtemplates/partner/application_remark_update.html', {
        'application': application,
        'remark': app_remark.message,
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[partner_email],
        fail_silently=False,
        html_message=message  # Use HTML content for rich formatting
    )
