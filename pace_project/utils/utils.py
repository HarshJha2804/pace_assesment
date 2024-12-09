from pace_project.core.models.core_models import StatusType
from pace_project.paceapp.enums import RoleEnum
from pace_project.paceapp.models import University
from pace_project.users.models import Role, Employee
from django.db.models import QuerySet
from django.contrib.auth import get_user_model

User = get_user_model()


def get_superuser_list(full_details: bool = False) -> QuerySet[User]:
    """
    Fetches the list of superusers.

    :param full_details: If True, fetches all fields of the superuser.
                         If False, only fetches 'id' and 'email'.
    :return: QuerySet of User objects.
    """
    queryset = User.objects.filter(is_superuser=True)

    if not full_details:
        # Return only essential fields when full details are not needed
        queryset = queryset.only('id', 'email')

    return queryset


def get_partner_role_obj():
    role_obj = Role.objects.filter(name__exact=RoleEnum.PARTNER.value).first()
    return role_obj


def get_partner_onboarding_officer(full_details: bool = False):
    obj = User.objects.filter(role__name__exact=RoleEnum.PARTNER_ONBOARDING_OFFICER.value).first()
    if not full_details:
        obj.only("id", "email")

    return obj


def get_assessment_officer(*, university: University, full_details: bool = False):
    obj = Employee.objects.filter(
        assigned_universities=university, user__role__name=RoleEnum.ASSESSMENT_OFFICER.value,
        user__is_active=True
    ).first()
    if not full_details:
        obj.only("id", "user")
    return obj


def get_status_object(status_name):
    try:
        status_object = StatusType.objects.get(name=status_name)
    except StatusType.DoesNotExist:
        status_object = None
    return status_object
