from django.db.models import Count
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db import models

from pace_project.paceapp.models import University
from pace_project.users.models import Employee


class GenericDocumentManager(models.Manager):
    def get_deleted_documents(self):
        return self.filter(is_deleted=False)

    def get_documents_for_object(self, obj):
        """
        Retrieve documents associated with a given object, excluding soft-deleted ones.
        """
        return self.filter(
            object_id=obj.pk,
            content_type=ContentType.objects.get_for_model(obj),
            is_deleted=False
        )


class ApplicationAssignmentLogManager(models.Manager):

    def get_next_application_manager(self, university: University):
        today = timezone.now().date()

        # Get eligible managers for the given university
        eligible_managers = Employee.objects.get_eligible_managers(university)

        # Get the log of applications assigned today for the given university
        application_assigned_managers = self.filter(
            created__date=today,
            application__course__university=university
        )

        # Annotate eligible managers with the count of applications assigned today
        employee_assignment_counts = eligible_managers.annotate(
            log_count=Count(
                'assigned_application_logs',
                filter=models.Q(assigned_application_logs__in=application_assigned_managers)
            )
        )

        # Find the employee with the minimum count
        if employee_assignment_counts.exists():
            next_manager = min(employee_assignment_counts, key=lambda e: e.log_count)
            return next_manager
        return None

    def get_last_assigned_application_manager(self, university: University):
        """
        Return the last assigned application manager for the given university.
        You can implement this based on the most recent assignment log.
        """
        # Get the last assignment log for the university
        last_log = self.filter(application__course__university=university).order_by('-created').first()

        if last_log:
            return last_log.assigned_to
        return None
