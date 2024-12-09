from pace_project.core.mixins import INORequiredMixin
from django.views.generic import ListView

from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import UniversityInterviewStatus, StatusType


class INOApplicationListView(INORequiredMixin, ListView):
    model = Application
    paginate_by = 20
    template_name = "core/interview_officer/_list.html"

    def get_queryset(self):
        """
        Fetch applications that match the interview statuses of the universities
        assigned to the employee. Return an empty queryset if no status types are found.
        """
        passport_number = self.request.GET.get("passport_number")
        name = self.request.GET.get("name")
        status_id = self.request.GET.get("status")

        interview_statuses = self.get_interview_statuses()

        # Return an empty queryset if no interview statuses are available
        if not interview_statuses:
            return Application.objects.none()

        queryset = super().get_queryset()
        queryset = queryset.filter(
            current_status_id__in=interview_statuses, course__university__in=self.employee.get_assigned_universities
        )

        if passport_number:
            queryset = queryset.filter(student__passport_number__istartswith=passport_number)

        if name:
            queryset = queryset.filter(student__first_name__istartswith=name)

        if status_id:
            queryset = queryset.filter(current_status_id=status_id)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['interview_statuses'] = StatusType.objects.filter(id__in=self.get_interview_statuses())
        return ctx
