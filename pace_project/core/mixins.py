from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.views.generic import View

from pace_project.core.models.core_models import UniversityInterviewStatus
from pace_project.paceapp.enums import RoleEnum
from pace_project.users.models import Employee


class EmployeeRequiredMixin(View):

    @cached_property
    def employee(self):
        return self.get_employee_profile()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            if self.employee:
                return super().dispatch(request, *args, **kwargs)
            else:
                raise PermissionDenied("Warning: Your account does not have an associated employee profile.")
        else:
            raise PermissionDenied("You do not have staff permissions.")

    def get_employee_profile(self):
        try:
            return self.request.user.employee
        except Employee.DoesNotExist:
            return None


class SuperuserRequiredMixin(EmployeeRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.user.is_superuser:
            return response
        else:
            raise PermissionDenied("You do not have access.")


class RMHRequiredMixin(EmployeeRequiredMixin):
    """
      Mixin to ensure the user is a Regional Marketing Head (RMH) and has an associated employee profile.
      Inherits from EmployeeRequiredMixin to check for staff status and employee profile.
      """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.name == RoleEnum.REGIONAL_MARKETING_HEAD.value:
            return response
        else:
            raise PermissionDenied("You do not have access.")


class ASFRequiredMixin(EmployeeRequiredMixin):
    """
    Mixin to ensure the user is an Assessment Officer (ASF).
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.name == RoleEnum.ASSESSMENT_OFFICER.value:
            return response
        else:
            raise PermissionDenied("You do not have access.")


class AMRequiredMixin(EmployeeRequiredMixin):
    """
    Mixin to ensure the user is an Application Manager (AM).
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.name == RoleEnum.APPLICATION_MANAGER.value:
            return response
        else:
            raise PermissionDenied("You do not have access.")


class INORequiredMixin(EmployeeRequiredMixin):
    """
    Mixin to ensure the user is an Interview Officer (INO).
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.name == RoleEnum.INTERVIEW_OFFICER.value:
            return response
        else:
            raise PermissionDenied("You do not have access.")

    def get_interview_statuses(self):
        """
        Retrieve all interview statuses associated with the assigned universities of the employee.
        Optimized by using 'prefetch_related' to avoid multiple database hits and
        'values_list' for more efficient querying.

        Return type list of status types id's.
        """
        assigned_universities = self.employee.assigned_universities.all()

        # Fetch all related interview statuses in one query
        statuses = UniversityInterviewStatus.objects.filter(
            university__in=assigned_universities, is_active=True
        ).prefetch_related('status_types')

        # Accumulate the unique status types from all universities
        status_types = set()
        for uis in statuses:
            status_types.update(uis.status_types.values_list('id', flat=True))

        return list(status_types)


class CMPORequiredMixin(EmployeeRequiredMixin):
    """
    Mixin to ensure the user is a compliance officer (CMPO).
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.name == RoleEnum.COMPLIANCE_OFFICER.value:
            return response
        else:
            raise PermissionDenied("You do not have access.")


class DMORequiredMixin(EmployeeRequiredMixin):
    """
    Mixin to ensure the user is a Data Management officer (DMO).
    """
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.name == RoleEnum.DATA_MANAGEMENT_OFFICER.value:
            return response
        else:
            raise PermissionDenied("You do not have access.")
