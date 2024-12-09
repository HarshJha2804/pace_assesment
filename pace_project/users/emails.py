import logging

from pace_project.users.models import Partner
from django.conf import settings
from django.template.loader import render_to_string
from pace_project.utils.utils import get_partner_onboarding_officer, get_superuser_list
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def mail_to_superuser(*, subject: str, partner: Partner):
    try:
        superusers = get_superuser_list().values_list('email', flat=True)
        onboarded_officer = get_partner_onboarding_officer(full_details=True)
        recipient_list = list(superusers)  # Convert queryset to list
        if onboarded_officer:
            recipient_list.append(onboarded_officer.email)
        from_mail = settings.DEFAULT_FROM_EMAIL
        context = {
            'partner': partner,
            "email": partner.email,
            "country_code": partner.country.country_code,
            "mobile": partner.mobile_number,
            "contact_person": partner.contact_name,
            "address": partner.get_full_address,
        }

        subject = f"New Partner {partner.company_name} from {partner.country} has successfully registered on portal"
        email_message = render_to_string("emailtemplates/new_partner_onboarding_confirmation_email_to_admin.html",
                                         context)
        send_mail(
            subject,
            email_message,
            from_email=from_mail,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=email_message
        )
    except Exception as e:
        logger.error(f"An error occurred while sending mail to superuser of partner creation: {e}", exc_info=True)


def mail_to_onboarding_officer(*, subject: str, partner: Partner):
    try:
        to = get_partner_onboarding_officer(full_details=True)
        if to and partner:
            onboarding_officer_mail = to.email
            from_mail = settings.DEFAULT_FROM_EMAIL
            message = (f"New Partner {partner.company_name} registered from {partner.country}!\nContact Person Name: "
                       f"{partner.contact_name}\nContact Email{partner.email}\n\nRegistered on {partner.created}")
            recipient_list = [onboarding_officer_mail]
            send_mail(
                subject=subject,
                message=message,
                from_email=from_mail,
                recipient_list=recipient_list,
                fail_silently=False,
            )
    except Exception as e:
        logger.error(f"An error occurred while sending mail to onboarding officer of partner creation: {e}", exc_info=True)
