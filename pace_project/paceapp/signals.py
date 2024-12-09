from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.core.cache import cache

from pace_project.paceapp.models import Country, University, Year, Intake
from pace_project.users.models import Role

User = get_user_model()


@receiver(post_save, sender=Country)
@receiver(post_delete, sender=Country)
def invalidate_country_cache(sender, **kwargs):
    cache.delete('countries')


@receiver(post_save, sender=University)
@receiver(post_delete, sender=University)
def invalidate_university_cache(sender, **kwargs):
    cache.delete('universities')


@receiver(post_save, sender=Year)
@receiver(post_delete, sender=Year)
def invalidate_year_cache(sender, **kwargs):
    cache.delete('years')


@receiver(post_save, sender=Intake)
@receiver(post_delete, sender=Intake)
def invalidate_intakes_cache(sender, **kwargs):
    cache.delete('intakes')


@receiver(post_save, sender=Role)
@receiver(post_delete, sender=Role)
def invalidate_role_cache(sender, **kwargs):
    cache.delete('roles')
