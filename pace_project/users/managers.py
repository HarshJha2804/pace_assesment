from typing import TYPE_CHECKING

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models

from pace_project.paceapp.enums import RoleEnum

if TYPE_CHECKING:
    from .models import User  # noqa: F401


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def _create_user(self, email: str, password: str | None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self._create_user(email, password, **extra_fields)

    def employees(self):
        return self.filter(is_staff=True)


class EmployeeManager(models.Manager):
    def available_employees(self):
        """
        Returns employees who are currently available (not on leave).

        Returns:
            QuerySet: A queryset of employees who are not on leave.
        """
        return self.filter(is_on_leave=False, user__is_active=True)

    def regional_marketing_heads(self):
        """
        Returns a queryset of employees who are regional marketing heads.
        The queryset is optimized with select_related and prefetch_related
        for better performance on related fields.
        """
        return (self.filter(user__role__name=RoleEnum.REGIONAL_MARKETING_HEAD.value).select_related(
            'user', 'assigned_country', 'mobile_country_code', 'whatsapp_country_code'
        ).prefetch_related('assigned_universities', 'assigned_regions'))

    def get_eligible_managers(self, university):
        """
        Retrieves eligible application managers for a given university.

        Parameters:
            university (University): The university to filter by.

        Returns:
            QuerySet: A queryset of eligible managers assigned to the university and not on leave.
        """
        return (
            self.filter(
                user__role__name=RoleEnum.APPLICATION_MANAGER.value,
                is_on_leave=False,
                assigned_universities=university
            )
            .select_related("user")
            .order_by("user__id")  # Consistent order for round-robin
        )


class PartnerManager(models.Manager):
    def active_partners(self):
        return self.filter(is_active=True)
