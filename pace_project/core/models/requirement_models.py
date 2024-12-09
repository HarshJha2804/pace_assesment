from django.db import models
from model_utils.models import TimeStampedModel


class StaffingRequirement(TimeStampedModel):
    """
    This model represents the staffing needs or requirements for achieving a target.
    """
    target_value = models.IntegerField()
    rm_count = models.IntegerField(help_text="Regional Marketing Head")
    assessment_officer_count = models.IntegerField()
    application_manager_count = models.IntegerField()
    interviewer_count = models.IntegerField()
    visa_officer_count = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.target_value)
