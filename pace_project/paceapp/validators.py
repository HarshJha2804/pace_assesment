from datetime import datetime

from pace_project.paceapp.enums import RoleEnum
from pace_project.users.models import ApplicationManager, Employee, Partner, PartnerAgreement


def is_superuser_or_has_permission(request):
    user = request.user
    if user.is_superuser or user.has_perm('users.view_partner'):
        return True


def has_student_permission(request):
    user = request.user
    if request.user.is_superuser:
        return False
    if user.has_perm('users.view_student'):
        return True
    return False


def has_application_permission(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role

    if user_role and user_role.name == RoleEnum.APPLICATION_MANAGER.value and not user.is_superuser:
        app_manager = user.employee.applicationmanager
        if app_manager.is_head and app_manager.will_process_application:
            return True
        elif not app_manager.is_head:
            return True
        else:
            return False


def is_application_manager(request):
    user = request.user
    if user.is_anonymous:
        return False

    user_role = user.role
    if user_role and user_role.name == RoleEnum.APPLICATION_MANAGER.value and not user.is_superuser:
        try:
            employee = user.employee
            application_manager = employee.applicationmanager
            if application_manager:
                return True
        except (Employee.DoesNotExist, ApplicationManager.DoesNotExist):
            return False
    return False


def has_application_permission_is_head(request):
    user = request.user
    if user.is_anonymous:
        return False

    user_role = user.role
    if user_role and user_role.name == RoleEnum.APPLICATION_MANAGER.value and not user.is_superuser:
        try:
            employee = user.employee
            application_manager = employee.applicationmanager
            if application_manager:
                return True

        except (Employee.DoesNotExist, ApplicationManager.DoesNotExist):
            return False

    return False


def has_application_manager_permission_dashboard(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.APPLICATION_MANAGER.value and not user.is_superuser:
        return True
    return False


def has_application_manager_reports(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.APPLICATION_MANAGER.value and not user.is_superuser:
        return True
    return False


def has_regional_permission(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.REGIONAL_MARKETING_HEAD.value and not user.is_superuser:
        return True
    return False


def has_interview_permission(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.INTERVIEW_OFFICER.value and not user.is_superuser:
        return True
    return False


def has_compliance_officer_permission(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.COMPLIANCE_OFFICER.value and not user.is_superuser:
        return True
    return False


def has_assessment_permission(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.ASSESSMENT_OFFICER.value and not user.is_superuser:
        return True
    return False


def has_data_management_officer(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.DATA_MANAGEMENT_OFFICER.value and not user.is_superuser:
        return True
    return False


def has_partner(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.PARTNER.value and not user.is_superuser:
        return True
    return False


def has_partner_upload_agreements(request):
    user = request.user
    current_year = datetime.now().year
    if user.is_anonymous:
        return False

    user_role = user.role
    if user_role and user_role.name == RoleEnum.PARTNER.value and not user.is_superuser:
        try:
            partner = Partner.objects.get(user=request.user)
            partner_agreement = PartnerAgreement.objects.filter(partner__user=user, year=current_year).exists()
            if partner_agreement:
                return False
            if partner.is_agreement_sent:
                return True
        except (Employee.DoesNotExist, Partner.DoesNotExist):
            return False
    return False


def has_partner_download_agreements(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    current_year = datetime.now().year

    if user_role and user_role.name == RoleEnum.PARTNER.value and not user.is_superuser:
        try:
            partner_agreement = PartnerAgreement.objects.filter(partner__user=user, year=current_year).exists()
            if partner_agreement:
                return True
        except (Employee.DoesNotExist, Partner.DoesNotExist):
            return False
    return False


def has_mfa_auth(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.PARTNER.value and not user.is_superuser:
        return False
    else:
        return True


def has_onboarding_officer(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.PARTNER_ONBOARDING_OFFICER.value and not user.is_superuser:
        return True
    return False


def has_vice_president(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role
    if user_role and user_role.name == RoleEnum.VICE_PRESIDENT.value and not user.is_superuser:
        return True
    return False


def has_partner_account_permission(request):
    user = request.user
    if user.is_anonymous:
        return False
    user_role = user.role

    if user_role and user_role.name == RoleEnum.PARTNER_ACCOUNT_MANAGER.value and not user.is_superuser:
        return True
    return False
