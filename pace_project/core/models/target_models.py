from django.db import models
from model_utils.models import TimeStampedModel

from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import CountrySpecificStatus, StatusType
from pace_project.paceapp.models import University, Intake, Year
from pace_project.users.models import Employee, Partner


class UniversityTarget(TimeStampedModel):
    """Set a target for each university."""

    university = models.ForeignKey(University, on_delete=models.CASCADE)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)
    target = models.IntegerField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.university)


class RMTarget(TimeStampedModel):
    """Regional Marketing Head targets."""
    rm = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)
    target = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.rm)

    @property
    def total_applications(self):
        assigned_universities = self.rm.assigned_universities.filter(is_active=True)
        return Application.objects.filter(
            is_active=True,
            student__partner=self.partner,
            course__university__in=assigned_universities
        ).count()

    @property
    def get_achieved_count(self):
        assigned_country = self.rm.assigned_country
        country_specific_status = CountrySpecificStatus.objects.filter(country=assigned_country).first()
        achievement_status_ids = country_specific_status.achievement_statuses.filter(
            is_active=True).values_list('id', flat=True)
        count = Application.objects.filter(
            is_active=True,
            student__partner=self.partner,
            current_status__in=achievement_status_ids
        ).count()
        return count

    @property
    def balance_target(self):
        achieved = self.get_achieved_count
        target = self.target
        return target - achieved


class RMUniversityIntake(TimeStampedModel):
    """Regional Marketing Head intakes university wise."""
    rm = models.ForeignKey(Employee, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.rm.user.name)
