from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from notifications.signals import notify
from notifications.models import Notification

from .emails import mail_to_superuser, mail_to_onboarding_officer
from .middlewares import get_current_request
from .models import Partner, PartnerBranch, Student
from pace_project.utils.utils import get_superuser_list
from django.core.cache import cache

User = get_user_model()


@receiver(post_save, sender=Partner)
def create_or_update_partner_branch(sender, instance, created, **kwargs):
    if created:
        # Create a new PartnerBranch instance when a Partner is created
        PartnerBranch.objects.create(
            partner=instance,
            name=f"{instance.company_name} - Head Office",
            is_head_office=True,
            country=instance.country,
            state=instance.state,
            city=instance.city,
            pincode=instance.pincode,
            address=instance.address,
            is_active=instance.is_active
        )
        notify_on_partner_creation(partner=instance)
    else:
        # Update the existing PartnerBranch instance when a Partner is updated
        branch = PartnerBranch.objects.filter(partner=instance, is_head_office=True).first()
        if branch:
            branch.country = instance.country
            branch.state = instance.state
            branch.city = instance.city
            branch.pincode = instance.pincode
            branch.address = instance.address
            branch.is_active = instance.is_active
            branch.save()


@receiver(post_save, sender=Student)
def notify_on_student_creation(sender, instance, created, **kwargs):
    if created:
        superuser_list = get_superuser_list()
        request = get_current_request()
        logged_in_user = request.user
        verb_msg = f"New Student {instance.get_full_name.upper()} added for Partner {str(instance.partner).upper()}"
        notify.send(logged_in_user, recipient=superuser_list, verb=verb_msg, action_object=instance)


def notify_on_partner_creation(*, partner: Partner):
    superuser_list = get_superuser_list()
    request = get_current_request()
    if request and request.user.is_authenticated:
        logged_in_user = request.user
        verb_msg = f"New Partner {partner.company_name.upper()} onboarded from {str(partner.country).upper()}!"
        mail_to_superuser(subject=verb_msg, partner=partner)
        mail_to_onboarding_officer(subject=verb_msg, partner=partner)
        notify.send(logged_in_user, recipient=superuser_list, verb=verb_msg, action_object=partner)
    else:
        verb_msg = f"New Partner {partner.company_name.upper()} registered from {str(partner.country).upper()}!"
        mail_to_superuser(subject=verb_msg, partner=partner)
        notify.send(partner.user, recipient=superuser_list, verb=verb_msg, action_object=partner)


@receiver(post_save, sender=User)
def clear_cache_on_user_avatar_update(sender, instance, **kwargs):
    cache_key = f"user_avatar_{instance.id}"
    cache.delete(cache_key)  # Invalidate the cache when the image is updated


@receiver(post_delete, sender=Notification)
@receiver(post_save, sender=Notification)
def invalidate_notification_cache(sender, instance, **kwargs):
    # Invalidate cache for the user who received a new notification
    cache_key = f"user_notifications_{instance.recipient.id}"
    cache.delete(cache_key)


@receiver(post_save, sender=Partner)
@receiver(post_delete, sender=Partner)
def invalidate_partner_cache(sender, **kwargs):
    cache.delete('partners')
