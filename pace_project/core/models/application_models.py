from django.db import models
from django_lifecycle import LifecycleModelMixin, hook, AFTER_UPDATE, AFTER_CREATE
from django_lifecycle.conditions import WhenFieldHasChanged
from model_utils.models import TimeStampedModel
from pace_project.core.enums import StatusTypeEnum
from pace_project.core.managers import ApplicationAssignmentLogManager
from pace_project.core.models.core_models import StatusType, DynamicField, InterviewStatusType, Condition
from pace_project.core.services import create_application_status_log
from pace_project.paceapp.models import Course, Intake, Year
from pace_project.users.models import Student, Employee
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Application(LifecycleModelMixin, TimeStampedModel):
    """
    Application of a student to a specific course with associated status.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    OFFER_STATUS_CHOICES = [
        ('CO', 'CO'),
        ('UC', 'UC'),
    ]
    COMPANY_APPLIED_THROUGH_CHOICES = [
        ('INFINITE', 'INFINITE'),
        ('Visa Global', 'Visa Global'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    current_status = models.ForeignKey(StatusType, on_delete=models.SET_NULL, null=True)
    conditions = models.ManyToManyField(Condition, blank=True)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='applications_created')
    medical_status = models.CharField(max_length=30, choices=STATUS_CHOICES, null=True, blank=True)
    funds_status = models.CharField(max_length=30, choices=STATUS_CHOICES, null=True, blank=True)
    offer_status = models.CharField(max_length=30, choices=OFFER_STATUS_CHOICES, null=True, blank=True)
    company_applied_through = models.CharField(max_length=30, choices=COMPANY_APPLIED_THROUGH_CHOICES, null=True,
                                               blank=True)
    offer_id = models.CharField(max_length=50, null=True, blank=True)
    tuition_fee_paid = models.CharField(max_length=50, null=True, blank=True)
    tuition_fee_for_enrollment = models.CharField(max_length=50, null=True, blank=True)
    balance_tuition_fee = models.CharField(max_length=50, null=True, blank=True)
    interview_status = models.ForeignKey(
        InterviewStatusType, on_delete=models.SET_NULL, null=True,
        blank=True, help_text="University Interview status"
    )
    application_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications'
    )

    class Meta:
        indexes = [
            models.Index(fields=['course']),  # Indexing course for query optimization
        ]

    def __str__(self):
        return str(self.student)

    def get_status_log_by_status(self, status_name):
        return ApplicationStatusLog.objects.filter(application=self, status__name__iexact=status_name).first()

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE, condition=WhenFieldHasChanged('current_status', has_changed=True))
    def generate_status_log(self):
        create_application_status_log(application=self, status=self.current_status)

    @property
    def get_application_submitted_by(self):
        status_object = ApplicationStatusLog.objects.filter(
            application=self,
            status__name__exact=StatusTypeEnum.APPLICATION_SUBMITTED.value).first()
        if status_object:
            return status_object.created_by.name
        return "-"

    @property
    def get_absolute_url(self):
        return reverse("core:application_detail", kwargs={"pk": self.pk})

    def get_notification_url(self, user):
        if user.is_partner:
            return self.get_partner_absolute_url
        else:
            return self.get_absolute_url

    @property
    def get_am_absolute_url(self):
        return reverse('paceapp:student_detail', kwargs={'pk': self.student.pk})

    @property
    def get_remarks(self):
        return ApplicationRemark.objects.filter(application=self)

    @property
    def get_status_logs(self):
        return ApplicationStatusLog.objects.filter(application=self)

    @property
    def get_attributes(self):
        return ApplicationAttribute.objects.filter(application=self)

    @property
    def get_student_absolute_url(self):
        return reverse('partner:partner_student_detail', kwargs={'pk': self.student.pk})

    @property
    def get_student_document_upload_url(self):
        if self.student:
            return reverse("paceapp:upload_student_document", kwargs={"pk": self.student.pk})
        return None

    @property
    def get_partner_absolute_url(self):
        return reverse("partner:application_detail", kwargs={"pk": self.pk})

    @property
    def get_pending_from_partner_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.APPLICATION_PENDING_FROM_AGENT.value)
        return getattr(obj, "created", None)

    @property
    def get_pending_from_ig_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value)
        return getattr(obj, "created", None)

    @property
    def get_submitted_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.APPLICATION_SUBMITTED.value)
        return getattr(obj, "created", None)

    @property
    def get_conditional_letter_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.CONDITIONAL_OFFER_LETTER.value)
        return getattr(obj, "created", None)

    @property
    def get_unconditional_letter_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.UNCONDITIONAL_OFFER_LETTER.value)
        return getattr(obj, "created", None)

    @property
    def get_fee_paid_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.FEE_PAID.value)
        return getattr(obj, "created", None)

    @property
    def get_cas_received_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.CAS_RECEIVED.value)
        return getattr(obj, "created", None)

    @property
    def get_cas_applied_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.CAS_APPLIED.value)
        return getattr(obj, "created", None)

    @property
    def get_rejected_by_ig_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.APPLICATION_REJECTED_BY_IOA.value)
        return getattr(obj, "created", None)

    @property
    def get_visa_lodged_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.VISA_LODGED.value)
        return getattr(obj, "created", None)

    @property
    def get_visa_granted_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.VISA_GRANT.value)
        return getattr(obj, "created", None)

    @property
    def get_visa_refused_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.VISA_REFUSED.value)
        return getattr(obj, "created", None)

    @property
    def get_prescreening_rejected_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.PRESCREENING_REJECTED.value)
        return getattr(obj, "created", None)

    @property
    def get_prescreening_approved_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.PRESCREENING_APPROVED.value)
        return getattr(obj, "created", None)

    @property
    def get_prescreening_pending_date(self):
        obj = self.get_status_log_by_status(status_name=StatusTypeEnum.PRESCREENING_PENDING.value)
        return getattr(obj, "created", None)


class ApplicationStatusLog(TimeStampedModel):
    """
    Tracks the status history of an application.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_logs')
    status = models.ForeignKey(StatusType, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.application.course and self.status:
            return f"{self.application.course.name} {self.status.name}"
        elif self.status:
            return f"{self.status.name}"
        elif self.application.course:
            return f"{self.application.course.name}"
        else:
            return super().__str__()

    class Meta:
        indexes = [
            models.Index(fields=['application', 'status']),
        ]
        ordering = ['-created']

    @property
    def get_previous_status(self):
        """
        Returns the previous status log entry for the same application.
        """
        previous_log = (
            ApplicationStatusLog.objects
            .filter(application=self.application, created__lt=self.created)
            .order_by('-created')
            .first()
        )
        return previous_log.status if previous_log else None


class ApplicationAssignmentLog(TimeStampedModel):
    """
    Log history of application assignments to employees.
    Tracks each time an application is assigned or reassigned.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='assignment_logs')
    assigned_to = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, related_name='assigned_application_logs'
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who assigned the application"
    )
    objects = ApplicationAssignmentLogManager()

    def __str__(self):
        return f"Application {self.application.id} assigned to {self.assigned_to} on {self.created}"

    class Meta:
        ordering = ['-created']


class ApplicationRemark(TimeStampedModel):
    """
    Tracks remarks and action messages for an application.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='remarks')
    message = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Remark by {self.author.name if self.author else 'Unknown'} on {str(self.application.student)}"

    class Meta:
        indexes = [
            models.Index(fields=['application', 'author']),
        ]
        ordering = ['-created']
        get_latest_by = 'created'

    def get_notification_url(self, user):
        if user.is_partner:
            return self.application.get_partner_absolute_url
        else:
            return self.application.get_absolute_url


class ApplicationAttribute(TimeStampedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='attributes')
    field = models.ForeignKey(DynamicField, on_delete=models.SET_NULL, null=True, related_name="application_attributes")
    value = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='attributes_created')

    def __str__(self):
        return self.application.student.get_full_name

    class Meta:
        indexes = [
            models.Index(fields=['application', 'field'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['application', 'field'], name='unique_application_key')
        ]


class InterviewActivity(TimeStampedModel):
    """Tracks interview-related activities for applications."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interview_activities")
    interview_status = models.ForeignKey(InterviewStatusType, on_delete=models.CASCADE)
    activity_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
