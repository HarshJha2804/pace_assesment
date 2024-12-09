import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from pace_project.users.middlewares import get_current_request

# Configure logging
logger = logging.getLogger(__name__)


def create_application_status_log(*, application, status):
    from pace_project.core.models.application_models import ApplicationStatusLog
    instance = ApplicationStatusLog.objects.create(
        application=application, status=status
    )
    request = get_current_request()
    if request.user and not request.user.is_anonymous:
        instance.created_by = request.user
        instance.save()


def assign_application_manager(application):
    """
    Assigns the next available application manager to an application using round-robin distribution.
    Logs the process and handles errors gracefully without raising exceptions.

    :param application: Application instance to be assigned
    :return: Assigned manager instance or None if assignment failed
    """
    # Validate essential data
    if not application.course or not application.course.university:
        logger.error("Application course or university is missing for application ID %s.", application.pk)
        return None

    try:
        with transaction.atomic():
            university = application.course.university

            # Get the next application manager in round-robin order
            from pace_project.core.models.application_models import ApplicationAssignmentLog
            next_manager = ApplicationAssignmentLog.objects.get_next_application_manager(university)
            if not next_manager:
                logger.warning("There is no application managers available for university %s", university.name)
                return None

            # Assign the application manager to the application
            application.application_manager = next_manager.user
            application.save()

            # Log the assignment in the ApplicationAssignmentLog for tracking
            ApplicationAssignmentLog.objects.create(application=application, assigned_to=next_manager)
            return next_manager  # Return the assigned manager for further processing if needed

    except ObjectDoesNotExist as e:
        logger.error("Data referenced by the application does not exist. Error: %s", str(e))
        return None

    except Exception as e:
        # Log unexpected issues and allow the function to return None
        logger.exception("Unexpected error during application manager assignment for application ID %s", application.pk)
        return None
