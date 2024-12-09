from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django.db.models import CharField
from pace_project.paceapp.models import University, Intake, Year, Country, Level, AssessmentDiscovery, State
from pace_project.users.models import Student
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField

User = get_user_model()


class Organization(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']


class CommissionStructure(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, help_text="partner country")
    university = models.ForeignKey(University, null=True, on_delete=models.SET_NULL)
    year = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL)
    commission = models.FloatField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.country} - {self.university} - {self.year}"


class DocumentTemplate(TimeStampedModel):
    """
    Master list of document templates.
    """
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PartnerSupportDocument(TimeStampedModel):
    """
    Documents required by university for each intake period.
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='documents/')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.university} - {self.template}"

    @property
    def get_document_url(self):
        url = None
        if self.file.url:
            url = self.file.url
        return url


class StatusType(TimeStampedModel):
    """
    Definition representing various statuses with associated priority.
    """
    name = models.CharField(_('Status Name'), max_length=255, unique=True)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['priority']  # Order by priority in ascending order

    def __str__(self):
        return self.name


class InterviewStatusType(TimeStampedModel):
    """
    Interview Status Type definition.
    """
    name = models.CharField(_('Status Name'), max_length=255, unique=True)
    is_mock = models.BooleanField(default=False, help_text="Mark This Status Type as Mock interview Status Type")
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return self.name

    def get_update_url(self):
        return reverse("core:update_interview_status_type", kwargs={'pk': self.pk})


class CountrySpecificStatus(TimeStampedModel):
    """
    Statuses applicable to a specific country.
    """
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    status_types = models.ManyToManyField(StatusType, related_name='country_specific_statuses')
    achievement_statuses = models.ManyToManyField(StatusType, related_name='achievements')
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['country']),  # Indexing country for query optimization
        ]

    def __str__(self):
        return self.country.country_name if self.country else "No Country"

    @property
    def get_absolute_url(self):
        return reverse(
            "core:country_specific_status_detail", kwargs={"pk": self.pk}
        )

    @property
    def get_update_url(self):
        return reverse(
            "core:update_country_specific_status", kwargs={"pk": self.pk}
        )

    @property
    def get_delete_url(self):
        return "#"


class Condition(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UniversityInterviewStatus(TimeStampedModel):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='interview_statuses')
    status_types = models.ManyToManyField(StatusType, related_name='university_interview_statuses')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "University Interview Status"
        verbose_name_plural = "University Interview Statuses"
        indexes = [
            models.Index(fields=['university', 'is_active']),
        ]

    def __str__(self):
        return f"{self.university.name} Interview Status"


class CountrySpecificDocument(TimeStampedModel):
    """
    Documents to a specific country.
    """
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    document_types = models.ManyToManyField(DocumentTemplate, related_name='country_specific_documents')
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['country']),  # Indexing country for query optimization
        ]

    def __str__(self):
        return self.country.country_name if self.country else "No Country"

    @property
    def get_absolute_url(self):
        return reverse(
            "core:country_specific_document_detail", kwargs={"pk": self.pk}
        )

    @property
    def get_update_url(self):
        return reverse(
            "core:update_country_specific_document", kwargs={"pk": self.pk}
        )

    @property
    def get_delete_url(self):
        return "#"


class CountrySpecificLevel(TimeStampedModel):
    """
    Levels to a specific country.
    """
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    levels = models.ManyToManyField(Level, related_name='country_specific_levels')
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return self.country.country_name if self.country else "No Country"

    @property
    def get_absolute_url(self):
        return reverse(
            "core:country_specific_level_detail", kwargs={"pk": self.pk}
        )


class DynamicField(TimeStampedModel):
    """
    Model representing a type of dynamic field that can be used in various contexts.
    """
    name = models.CharField(max_length=60)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def slug(self):
        """
        Returns a slugified version of the name field.
        """
        return slugify(self.name)

    @property
    def slugified_name(self):
        """
        Returns a slugified version of the name with underscores instead of hyphens.
        """
        return slugify(self.name).replace('-', '_')


class CountrySpecificField(TimeStampedModel):
    """
    Model representing a mapping between countries and dynamic fields that are applicable to that country.
    """
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    fields = models.ManyToManyField(DynamicField, related_name='country_specific_fields')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Fields for {self.country.country_name}"

    @property
    def get_absolute_url(self):
        return reverse(
            "core:country_specific_field_detail", kwargs={"pk": self.pk}
        )

    class Meta:
        verbose_name = 'Country Field Mapping'
        verbose_name_plural = 'Country Field Mappings'


class WorkExperience(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company_name = models.CharField(_("Company Name"), max_length=255)
    designation = models.CharField(_("Designation"), max_length=255)
    company_location = models.CharField(_("Company Location"), max_length=255)
    joined_date = models.DateField(_("Joined Date"))
    reliving_date = models.DateField(_("Reliving Date"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student.first_name


class AssessmentRequest(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    assessment = models.ForeignKey(AssessmentDiscovery, on_delete=models.SET_NULL, null=True, blank=True)
    assessment_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["student", "university", "is_active"]

    def __str__(self):
        return f"Request by {self.student.partner} for {self.university}"

    @property
    def is_assessment_provided(self):
        return self.assessment_officer is not None

    @property
    def get_student_absolute_url(self):
        return reverse('partner:partner_student_detail', kwargs={'pk': self.student.pk})

    @property
    def student_absolute_url(self):
        return reverse('paceapp:student_detail', kwargs={'pk': self.student.pk})


class PartnerOnBoardingRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('follow-up', 'Follow-up'),
        ('not-interested', 'Not Interested'),
        ('interested', 'Interested'),
    ]
    company_name = CharField(max_length=255, unique=True, help_text="Company Name")
    legal_name = CharField(max_length=255, null=True, help_text="Registered Company Name")
    contact_name = CharField(_("Contact Person Name"), max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    mobile_country_code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="mobile_country_code"
    )
    mobile_number = CharField(null=True, blank=True)

    whatsapp_country_code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="whatsapp_country_code"
    )
    whatsapp_number = CharField(null=True, blank=True)

    company_type = CharField(max_length=255, null=True, blank=True)
    office_type = CharField(max_length=255, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)

    owner_name = CharField(max_length=50, null=True, blank=True)
    owner_email = models.EmailField(null=True, blank=True)
    owner_mobile_number = CharField(max_length=20, null=True, blank=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)

    date_of_commencement = models.DateField(null=True, blank=True)
    logo = models.FileField(upload_to='partner_onboarding/logo', null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True, help_text="Partner website link.")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    on_boarded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="partner_onboarding"
    )
    onboarding_completed = models.BooleanField(default=False)

    is_agreement_sent = models.BooleanField(default=False)

    is_any_branch = models.BooleanField(default=False)
    number_of_branch = CharField(max_length=255, null=True, blank=True)
    target_for_next_intake = CharField(max_length=255, null=True, blank=True)

    blacklisted = models.BooleanField(default=False)
    remark = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['company_name', 'email', 'mobile_number']),
        ]

    def __str__(self):
        return self.company_name

    @property
    def get_logo_url(self):
        url = ''
        if self.logo:
            url = self.logo.url
        return url

    @property
    def get_initials(self):
        parts = self.company_name.split()
        return ''.join([part[0].upper() for part in parts])

    @property
    def get_mobile_number(self):
        if self.mobile_number and self.mobile_country_code:
            return f'{self.mobile_country_code.country_code}{self.mobile_number}'
        elif self.mobile_number:
            return f'{self.mobile_number}'
        else:
            return None

    @property
    def get_whatsapp_number(self):
        if self.whatsapp_number and self.whatsapp_country_code:
            return f'{self.whatsapp_country_code.country_code}{self.whatsapp_number}'
        elif self.whatsapp_number:
            return f"{self.whatsapp_number}"
        else:
            return None

    @property
    def get_full_address(self):
        address_parts = [
            self.address or '',
            self.city or '',
            self.pincode or '',
            str(self.state) or '',
            str(self.country) or ''
        ]
        # Join only the non-empty parts and separate by comma
        return ', '.join(filter(bool, address_parts))

    @property
    def get_partner_onboarding_url(self):
        return reverse('paceapp:onboarded_partner_detail', kwargs={'pk': self.pk})


class UpdateNews(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, help_text="update country")
    image = models.FileField(upload_to='updates', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="created_updates")
    update = RichTextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.country}"

    @property
    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return None


class Webinar(TimeStampedModel):
    class WebinarFor(models.TextChoices):
        INTERNAL = "Internal Team", "Internal Team"
        EXTERNAL = "Partner", "Partner"

    MEDIUM_CHOICES = [
        ('zoom', 'Zoom'),
        ('microsoft teams', 'Microsoft Teams'),
    ]
    agenda = models.CharField(_("Agenda "), max_length=255, null=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="webinar")
    webinar_for = models.CharField(
        max_length=100, choices=WebinarFor.choices, default=WebinarFor.INTERNAL
    )
    medium = models.CharField(max_length=100, choices=MEDIUM_CHOICES, default="zoom")
    schedule = models.DateTimeField()
    meeting_link = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name="created_webinar", on_delete=models.SET_NULL)
    remark = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.agenda}"


class UniversityCommissionType(TimeStampedModel):
    commission_type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.commission_type


class StudentSlab(TimeStampedModel):
    from_student = models.IntegerField()
    to_student = models.IntegerField()

    def __str__(self):
        return f"{self.from_student} - {self.to_student}"


class CommissionFromUniversity(TimeStampedModel):
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    intake = models.ForeignKey(Intake, on_delete=models.CASCADE, null=True, blank=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)

    student_slab = models.ForeignKey(StudentSlab, on_delete=models.CASCADE)

    commission_type = models.ForeignKey(UniversityCommissionType, on_delete=models.CASCADE)
    commission_in_percent = models.FloatField(null=True, blank=True)
    commission_in_flat = models.FloatField(null=True, blank=True)
    bonus_in_flat = models.FloatField(null=True, blank=True)
    bonus_in_percentage = models.FloatField(null=True, blank=True)

    note = models.TextField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.university.name}"


class DailyProgressReport(TimeStampedModel):
    activity_date = models.DateField(null=True, blank=True)
    task_partner = models.CharField(max_length=255, null=True, blank=True)
    activity_description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.task_partner}"
