from django.db import models
from model_utils.models import TimeStampedModel

from pace_project.core.models.core_models import StudentSlab, UniversityCommissionType
from pace_project.paceapp.models import University, Intake, Year, Country, Region
from pace_project.users.models import Partner
from django.contrib.auth import get_user_model

User = get_user_model()


class PartnerCommission(TimeStampedModel):
    class CommissionType(models.TextChoices):
        FLAT = "Flat", "Flat"
        PERCENTAGE = "Percentage", "Percentage"

    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="partner_commissions")
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="partner_commissions")
    date = models.DateField()
    commission_type = models.CharField(
        max_length=100, choices=CommissionType.choices, default=CommissionType.PERCENTAGE
    )
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_by = models.ForeignKey(User, null=True, related_name="created_commissions", on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Commission for {self.partner} at {self.university} on {self.date}"

    class Meta:
        ordering = ['date']

    @property
    def end_date(self):
        # Return created_at as the end date, or you can customize the logic here
        return self.created


class PartnerCommissionSetup(TimeStampedModel):
    COMMISSION_TYPE_CHOICES = [
        ("net fee", "Net Fee"),
        ("grass fee", "Grass Fee"),
    ]
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="partner_commissions_university")
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    region = models.ManyToManyField(Region, related_name="partner_commissions_region", null=True, blank=True)

    commission_type = models.ForeignKey(UniversityCommissionType, on_delete=models.CASCADE,
                                        related_name="partner_commission_type")
    commission = models.CharField(max_length=100, null=True, blank=True)
    commission_on = models.CharField(max_length=100, choices=COMMISSION_TYPE_CHOICES)
    commission_frequency = models.CharField(max_length=100, choices=University.MEDIUM_CHOICES, null=True,
                                            blank=True)

    slabs = models.ForeignKey(StudentSlab, on_delete=models.CASCADE)

    bonus_type = models.ForeignKey(UniversityCommissionType, on_delete=models.CASCADE,
                                   related_name="partner_commissions_bonus_type")
    bonus = models.CharField(max_length=100, null=True, blank=True)

    tution_fee_for_commission = models.CharField(max_length=100, null=True, blank=True)

    comments = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, related_name="created_partner_commissions",
                                   on_delete=models.SET_NULL)

    def __str__(self):
        return f"Commission for {self.university.name} at {self.country.country_name}"
