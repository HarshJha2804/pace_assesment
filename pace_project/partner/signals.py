from allauth.account.signals import email_confirmed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib import messages
from django.core.cache import cache
from pace_project.paceapp.models import University, Country
from pace_project.users.models import Partner


@receiver(email_confirmed)
def handle_partner_agreement_email(request, email_address, **kwargs):
    """Send partnership agreement email when the user's email is confirmed."""
    try:
        partner = Partner.objects.get(email=email_address)
        if not partner.is_agreement_sent:
            if partner.send_agreement_email():
                messages.success(request, 'Your partnership agreement has been sent.')
            else:
                messages.error(request, 'Failed to send your partnership agreement.')
    except Partner.DoesNotExist:
        messages.error(request, 'Partner not found for the given email address.')


@receiver([post_save, post_delete], sender=University)
@receiver([post_save, post_delete], sender=Country)
def invalidate_partner_university_cache(sender, **kwargs):
    """Clear cache of Direct apply university list view "country with universities" of partner."""
    CACHE_KEY = "partner_countries_with_universities"
    cache.delete(CACHE_KEY)
