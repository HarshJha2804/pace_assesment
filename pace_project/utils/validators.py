from functools import partial

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from pace_project.users.models import Partner
from django.contrib.auth import get_user_model

User = get_user_model()


def file_size_validator(max_size_in_mb):
    """
    Returns a validator function with a predefined max size in MB.
    """
    return partial(validate_file_size, max_size_in_mb=max_size_in_mb)


def validate_file_size(value, max_size_in_mb):
    max_size = max_size_in_mb * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(_(f"File size should not exceed {max_size_in_mb}MB."))


def validate_company_unique_trade_name(value):
    if Partner.objects.filter(company_name=value).exists():
        raise ValidationError(
            _(f"Company name {value} already registered.")
        )


def validate_unique_legal_name(value, instance=None):
    qs = Partner.objects.filter(legal_name=value)
    if instance:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise ValidationError(
            _('A company with the legal name "%(value)s" already exists.'),
            params={'value': value},
        )


def validate_unique_company_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            _('A company with the company email "%(value)s" already registered.'),
            params={'value': value},
        )
