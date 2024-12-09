from typing import ClassVar

from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField, Sum
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_lifecycle import hook, AFTER_CREATE, LifecycleModelMixin, AFTER_UPDATE
from django_lifecycle.conditions import WhenFieldHasChanged
from model_utils.models import TimeStampedModel

from .managers import UserManager, EmployeeManager, PartnerManager
from .middlewares import get_current_request
from pace_project.paceapp.enums import LevelEnum, RoleEnum
from pace_project.paceapp.models import Country, State, Level, Board, Stream, SubStream, EnglishTestType, Year, \
    University, Region, AssessmentDiscovery
from django.db import models
from django.contrib import messages
from pace_project.utils.common_utils import get_status_template


class Role(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def assessment_officer_url(self):
        return reverse('paceapp:assessment_dashboard')

    @property
    def application_manager_dashboard_url(self):
        return reverse('paceapp:dashboard_application_manager')

    @property
    def regional_marketing_head_dashboard_url(self):
        return reverse('paceapp:dashboard_regional_marketing_head')

    @property
    def interview_officer_dashboard_url(self):
        return reverse('paceapp:dashboard_interview_officer')

    @property
    def compliance_officer_dashboard_url(self):
        return reverse('paceapp:dashboard_compliance_officer')


class User(AbstractUser):
    """
    Default custom user model for paceproject.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    avatar = models.ImageField(upload_to="users/avatars/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def __str__(self):
        if self.name:
            return self.name
        return super().__str__()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    @property
    def get_initials(self):
        parts = self.name.split()
        return ''.join([part[0].upper() for part in parts])

    @property
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    @property
    def is_partner(self):
        return self.role.name == RoleEnum.PARTNER.value


class Partner(LifecycleModelMixin, TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('follow-up', 'Follow-up'),
        ('not-interested', 'Not Interested'),
        ('interested', 'Interested'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    company_name = CharField(max_length=255, unique=True, help_text="Company Name")
    legal_name = CharField(max_length=255, null=True, help_text="Registered Company Name")
    contact_name = CharField(_("Contact Person Name"), max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    mobile_country_code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="partner_mobile_country_code"
    )
    mobile_number = CharField(null=True, blank=True)

    whatsapp_country_code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="partner_whatsapp_country_code"
    )
    whatsapp_number = CharField(null=True, blank=True)

    company_type = CharField(max_length=255, null=True, blank=True)
    office_type = CharField(max_length=255, null=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)

    owner_name = CharField(max_length=50, null=True, blank=True)
    owner_email = models.EmailField(null=True, blank=True)
    owner_mobile_number = CharField(max_length=20, null=True, blank=True)
    designation = CharField(_("Designation"), max_length=100, null=True, blank=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)

    date_of_commencement = models.DateField(null=True, blank=True)
    logo = models.FileField(upload_to='partner/logo', null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True, help_text="Partner website link.")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    on_boarded_by = models.ForeignKey(
        "User", on_delete=models.CASCADE, null=True, blank=True, related_name="onboarding"
    )
    onboarding_completed = models.BooleanField(default=False)

    is_agreement_sent = models.BooleanField(default=False)

    blacklisted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = PartnerManager()

    class Meta:
        indexes = [
            models.Index(fields=['company_name', 'email', 'mobile_number']),
        ]

    def __str__(self):
        return self.company_name

    def send_agreement_email(self):
        """Send the partnership agreement email if not already sent."""
        if self.is_agreement_sent:
            return False
        from pace_project.users.services import send_partner_agreement_email
        result = send_partner_agreement_email(partner=self)
        if result:
            self.is_agreement_sent = True
            self.save()
        return result

    @hook(AFTER_UPDATE, condition=WhenFieldHasChanged('email', has_changed=True))
    def update_user_email(self):
        if self.user:
            self.user.email = self.email
            self.user.save()

    @property
    def get_absolute_url(self):
        return reverse('paceapp:partner_detail', kwargs={'pk': self.pk})

    @property
    def get_mark_not_interested_url(self):
        return reverse("users:mark_partner_not_interested", kwargs={'pk': self.pk})

    @property
    def get_mark_interested_url(self):
        return reverse("users:mark_partner_interested", kwargs={'pk': self.pk})

    @property
    def get_logo_url(self):
        if self.logo:
            return self.logo.url
        elif self.user:
            return self.user.get_avatar_url
        return None

    def get_notification_url(self, user=None):
        # TODO: If system provide login for partners then create property that return partner profile page.
        if self.get_absolute_url:
            return self.get_absolute_url
        else:
            request = get_current_request()
            messages.warning(request, "Something went wrong, with the notification detail of partner!")
            return reverse("users:redirect")

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
    def get_status(self):
        return get_status_template(is_active=self.is_active)

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

    @classmethod
    def get_list_url(cls):
        return reverse("paceapp:partner_list")

    @classmethod
    def get_add_url(cls):
        return reverse("paceapp:add_partner")

    @property
    def partner_account_manager(self):
        if not self.state or not self.state.region:
            return None

        region = self.state.region

        partner_account_manager = Employee.objects.filter(
            user__role__name=RoleEnum.PARTNER_ACCOUNT_MANAGER.value,
            assigned_regions=region
        ).first()

        return partner_account_manager

    @property
    def account_managers_in_region(self):
        from django.contrib.auth.models import User
        if self.state and self.state.region:  # Ensure the partner has an assigned region
            # Filter employees who are assigned to the partner's region and have the role 'Account Manager'
            account_managers = Employee.objects.filter(
                assigned_regions=self.state.region,
                user__role__name=RoleEnum.PARTNER_ACCOUNT_MANAGER.value
                # Adjust to match your role field value for Account Manager
            )
            return account_managers
        return Employee.objects.none()


class PartnerBranch(TimeStampedModel):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    name = CharField(_("Name of Branch"), max_length=255)
    is_head_office = models.BooleanField(default=False)

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)

    city = CharField(max_length=255, null=True, blank=True)
    pincode = CharField(max_length=255, null=True, blank=True)
    address = models.TextField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['partner', 'name', 'is_head_office', 'is_active']

    def __str__(self):
        return self.name


class PartnerCommunication(TimeStampedModel):
    COMMUNICATION_TYPE_CHOICES = [
        ('mobile', 'Mobile'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ]

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    branch = models.ForeignKey(PartnerBranch, on_delete=models.SET_NULL, null=True)
    communication_type = models.CharField(max_length=10, choices=COMMUNICATION_TYPE_CHOICES)
    communication_value = models.CharField(max_length=255)
    country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['partner', 'communication_type', 'communication_value']

    def __str__(self):
        return f"{self.get_communication_type_display()}: {self.communication_value}"

    @property
    def get_contact_value(self):
        if self.communication_type == 'email':
            return self.communication_value
        elif self.communication_type == 'whatsapp':
            return f"{self.country_code.country_code}{self.communication_value}"
        elif self.communication_type == 'mobile':
            return f"{self.country_code.country_code}{self.communication_value}"


class PartnerAgreement(TimeStampedModel):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    agreement = models.FileField(upload_to='partner/agreement')
    year = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.partner.company_name

    @property
    def get_agreement_url(self):
        if self.agreement:
            return self.agreement.url
        else:
            return None


class Student(TimeStampedModel):
    TYPE_CHOICES = [
        ('onshore', 'Onshore'),
        ('offshore', 'Offshore'),
    ]

    first_name = models.CharField(_("First Name"), max_length=255)
    middle_name = models.CharField(_("Middle Name"), max_length=255, null=True, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=255, null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(_("Email"), null=True, blank=True)
    mobile_number = models.CharField(_("Mobile Number"), max_length=20, null=True, blank=True)

    passport_number = models.CharField(_("Passport Number"), default='0', max_length=50, null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)

    study_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    study_country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_study_country"
    )

    type = models.CharField(_("Type of Student"), max_length=20, choices=TYPE_CHOICES, null=True, blank=True)

    assessment_status = models.ForeignKey(
        "core.StatusType", on_delete=models.SET_NULL, null=True, blank=True, related_name="student"
    )
    english_test_type = models.ForeignKey(
        EnglishTestType, on_delete=models.SET_NULL, null=True, blank=True, related_name="student"
    )
    assessment_requested = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="students_created")

    class Meta:
        unique_together = ('first_name', 'partner', 'date_of_birth', 'passport_number', 'study_country')

    @property
    def get_full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        if self.last_name:
            parts.append(self.last_name)
        full_name = " ".join(parts)
        return full_name

    def __str__(self):
        return self.get_full_name

    @property
    def get_absolute_url(self):
        return reverse('paceapp:student_detail', kwargs={'pk': self.pk})

    @property
    def get_student_absolute_url(self):
        return reverse('partner:partner_student_detail', kwargs={'pk': self.pk})

    def get_notification_url(self, user=None):
        request = get_current_request()
        if request.user.role.name == RoleEnum.PARTNER.value:
            return self.get_student_absolute_url
        elif request.user.is_staff and self.get_absolute_url:
            return self.get_absolute_url
        else:
            messages.warning(request, "Something went wrong, with the notification detail!")
            return reverse("users:redirect")

    def __is_ug_student(self):
        """Check if the student is classified as UG academic."""
        return self.study_level.level == LevelEnum.UNDERGRADUATE.value

    def __is_pg_student(self):
        """Check if the student is classified as PG academic."""
        return self.study_level.level == LevelEnum.POSTGRADUATE.value

    @property
    def get_academic_object(self):
        """Return the academic level (UG or PG) of the student."""
        if self.__is_ug_student():
            if UGStudentAcademic.objects.filter(student=self).exists():
                return UGStudentAcademic.objects.get(student=self)

        elif self.__is_pg_student():
            if PGStudentAcademic.objects.filter(student=self).exists():
                return PGStudentAcademic.objects.get(student=self)

        return None

    @property
    def get_discover_assessment_url(self):
        request = get_current_request()

        if not self.study_level:
            return reverse('paceapp:student_list')

        if self.study_level.level == LevelEnum.UNDERGRADUATE.value:
            return reverse('paceapp:discover_assessment')

        elif self.study_level.level == LevelEnum.POSTGRADUATE.value:
            return reverse('paceapp:discover_pg_assessment')

        else:
            messages.error(request, 'Something went wrong with level!')
            return reverse('paceapp:student_list')

    @property
    def get_add_academic_url(self):
        request = get_current_request()
        if not self.study_level:
            messages.warning(request, 'Please add student "Study Level" from update student!')
            return self.get_absolute_url

        if self.__is_ug_student():
            return reverse('users:add_ug_student_academic', kwargs={'pk': self.pk})

        elif self.__is_pg_student():
            return reverse('users:add_pg_student_academic', kwargs={'pk': self.pk})

        else:
            messages.error(request, f"For this Study Level, currently not defined add student academic!")
            return self.get_absolute_url

    @property
    def get_remarks(self):
        from pace_project.core.models.generic_models import GenericRemark
        return GenericRemark.objects.filter(object_id=self.pk, content_type=ContentType.objects.get_for_model(Student))

    @property
    def get_assessments(self):
        return AssessmentDiscovery.objects.filter(student=self)

    @property
    def get_applications(self):
        from pace_project.core.models.application_models import Application
        return Application.objects.filter(student=self)

    @property
    def get_document_upload_url(self):
        return reverse("paceapp:upload_student_document", kwargs={"pk": self.pk})

    @property
    def get_partner_document_upload_url(self):
        return reverse("partner:partner_upload_student_document", kwargs={"pk": self.pk})

    @property
    def get_document_types(self):
        if self.study_country:
            queryset = self.study_country.countryspecificdocument_set.all().first().document_types.all()
            return queryset
        return None

    @property
    def get_documents(self):
        from pace_project.core.models.generic_models import GenericDocument
        return GenericDocument.objects.get_documents_for_object(self)

    @property
    def get_partner_application_apply_url(self):
        return reverse("partner:partner_apply_application", kwargs={"pk": self.pk})

    @property
    def get_assessment_university_url(self):
        from pace_project.core.models.core_models import AssessmentRequest
        return AssessmentRequest.objects.filter(student=self).values_list('university__name', flat=True)


class StudentAcademic(TimeStampedModel):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, help_text="Country of Citizenship")

    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)

    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    sub_stream = models.ForeignKey(SubStream, on_delete=models.SET_NULL, null=True, blank=True)

    passing_month = models.IntegerField(null=True, blank=True)
    passing_year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)

    tenth_marks = models.IntegerField(null=True, blank=True)
    twelfth_english_marks = models.IntegerField(null=True, blank=True)

    english_test_type = models.ForeignKey(EnglishTestType, on_delete=models.SET_NULL, null=True, blank=True)
    english_overall = models.CharField(max_length=150, null=True, blank=True)
    speaking = models.CharField(max_length=150, null=True, blank=True)
    writing = models.CharField(max_length=150, null=True, blank=True)
    reading = models.CharField(max_length=150, null=True, blank=True)
    listening = models.CharField(max_length=150, null=True, blank=True)

    work_experience = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class UGStudentAcademic(StudentAcademic):
    ACADEMIC_PATHWAY_CHOICES = [
        ('diploma', 'Diploma'),
        ('intermediate', 'Intermediate'),
    ]

    academic_pathway = models.CharField(choices=ACADEMIC_PATHWAY_CHOICES, max_length=100, null=True, blank=True)

    overall_marks = models.IntegerField(null=True, blank=True, help_text="Twelfth/Diploma Overall marks")
    twelfth_math_marks = models.IntegerField(null=True, blank=True)
    twelfth_best_four_marks = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.student.get_full_name


class PGStudentAcademic(StudentAcademic):
    ACADEMIC_PATHWAY_CHOICES = [
        ('intermediate_ug', '12th And UG'),
        ('diploma_ug', 'Diploma And UG'),
        ('level_diploma', 'Diploma Level (6/7)'),
    ]

    academic_pathway = models.CharField(choices=ACADEMIC_PATHWAY_CHOICES, max_length=100, null=True, blank=True)

    diploma_overall_marks = models.IntegerField(null=True, blank=True)
    ug_overall_marks = models.IntegerField(null=True, blank=True)
    level_diploma_marks = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.student.get_full_name


class Employee(LifecycleModelMixin, TimeStampedModel):
    EMERGENCY_CONTACT_RELATION_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('wife', 'Wife'),
        ('husband', 'Husband'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_country_code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_mobile_country_code'
    )
    whatsapp_country_code = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_whatsapp_country_code'
    )
    mobile_number = models.CharField(_("Mobile Number"), max_length=20, null=True, blank=True)
    whatsapp_number = models.CharField(_("Whatsapp Number"), max_length=20, null=True, blank=True)
    emergency_mobile_number = models.CharField(_("Emergency Mobile Number"), max_length=20, null=True, blank=True)
    emergency_contact_relation = models.CharField(
        max_length=30, choices=EMERGENCY_CONTACT_RELATION_CHOICES, null=True, blank=True
    )
    assigned_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_universities = models.ManyToManyField(University, blank=True)
    assigned_regions = models.ManyToManyField(Region, blank=True)

    is_head = models.BooleanField(default=False)
    is_on_leave = models.BooleanField(default=False)
    objects = EmployeeManager()

    class Meta:
        indexes = [
            models.Index(fields=['mobile_number']),  # Index on mobile_number
            models.Index(fields=['whatsapp_number']),  # Index on whatsapp_number
            models.Index(fields=['assigned_country']),  # Index on assigned_country
            models.Index(fields=['user']),  # Index on user (for OneToOne relation)
        ]

    def __str__(self):
        return self.user.name

    @hook(AFTER_CREATE)
    def create_application_manager(self):
        """
        Creates a profile in the ApplicationManager model,
        when an employee with the role of Application Manager is added.
        """
        if self.user.role.name == RoleEnum.APPLICATION_MANAGER.value:
            ApplicationManager.objects.create(employee=self)

    def __is_regional_marketing_head(self):
        return getattr(self.user.role, 'name', None) == RoleEnum.REGIONAL_MARKETING_HEAD.value

    def __is_partner_account_manager(self):
        return getattr(self.user.role, 'name', None) == RoleEnum.PARTNER_ACCOUNT_MANAGER.value

    def __is_partner_account_manager_region(self):
        return getattr(self.user.role, 'name', None) == RoleEnum.PARTNER_ACCOUNT_MANAGER.value

    @property
    def get_set_rm_target_url(self):
        if self.__is_regional_marketing_head():
            return reverse("users:set_rm_target", kwargs={'pk': self.pk})
        return "#"

    @property
    def is_regional_marketing_head(self):
        return self.__is_regional_marketing_head()

    @property
    def get_set_rm_university_intake_url(self):
        if self.__is_regional_marketing_head():
            return reverse("users:set_rm_university_intake", kwargs={'pk': self.pk})
        return "#"

    @property
    def rm_target_count(self):
        if self.__is_regional_marketing_head():
            from pace_project.core.models.target_models import RMTarget
            total_target_count = RMTarget.objects.filter(
                rm=self, is_active=True
            ).aggregate(total=Sum('target'))['total'] or 0
            return total_target_count
        return 0

    @property
    def get_absolute_url(self):
        return reverse("users:employee_detail", kwargs={"pk": self.pk})

    @property
    def get_assign_region_url(self):
        if self.__is_regional_marketing_head():
            return reverse("users:assign_region", kwargs={"pk": self.pk})
        elif self.__is_partner_account_manager():
            return reverse("users:assign_region", kwargs={"pk": self.pk})
        else:
            return None

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
            return f'{self.whatsapp_number}'
        else:
            return None

    @property
    def get_assigned_regions(self):
        if self.assigned_regions:
            return self.assigned_regions.filter(is_active=True)
        return None

    @property
    def get_assigned_universities(self):
        return self.assigned_universities.filter(is_active=True)

    @property
    def get_list_url(self):
        return reverse("users:employee_list")

    @property
    def get_rm_list_url(self):
        return reverse("users:rm_list")

    @property
    def is_application_manager(self):
        try:
            return self.user.role.name == RoleEnum.APPLICATION_MANAGER.value and hasattr(self, 'applicationmanager')
        except AttributeError:

            return False

    @property
    def is_assessment_officer(self):
        try:
            return self.user.role.name == RoleEnum.ASSESSMENT_OFFICER.value
        except AttributeError:
            return False

    @property
    def has_compliance_officer_permission(self):
        return self.user.role.name == RoleEnum.COMPLIANCE_OFFICER.value


class ContactUs(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('replied', 'Replied'),
    ]

    subject = models.CharField(max_length=400)
    description = RichTextField(blank=True, null=True)
    connect_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_to')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    send_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_send')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.subject


class ApplicationManager(TimeStampedModel):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    is_head = models.BooleanField(default=False)
    will_process_application = models.BooleanField(default=False)

    def __str__(self):
        return self.employee.user.name
