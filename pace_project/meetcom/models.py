from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel

from pace_project.meetcom.managers import MeetingManager
from django.shortcuts import reverse

User = get_user_model()


class Meeting(TimeStampedModel):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
    ]

    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    scheduled_date = models.DateTimeField()

    assigned_to = models.ManyToManyField(User, related_name='assigned_meetings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    is_active = models.BooleanField(default=True)

    objects = MeetingManager()

    def __str__(self):
        return f'Meeting: {self.subject} scheduled on {self.scheduled_date.strftime("%Y-%m-%d %H:%M")}'

    class Meta:
        ordering = ['scheduled_date']
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'

    @property
    def get_absolute_url(self):
        return reverse(
            "meetcom:meeting_detail", kwargs={"pk": self.pk}
        )

    @property
    def get_rm_absolute_url(self):
        return reverse(
            "meetcom:rm_meeting_detail", kwargs={"pk": self.pk}
        )


class CommunicationType(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Communication(TimeStampedModel):
    communication_type = models.ForeignKey(CommunicationType, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=200)
    body = models.TextField(null=True, blank=True)
    related_meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, null=True, blank=True, related_name='communications'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communications')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.communication_type}: {self.subject}'

    class Meta:
        verbose_name = 'Communication'
        verbose_name_plural = 'Communications'


class CalendarEvent(TimeStampedModel):
    """
    Links a Google Calendar event to a specific meeting.

    Fields:
    - meeting: One-to-one relation with the Meeting model.
    - google_event_id: Unique ID of the event in Google Calendar.
    """
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name='calendar_event')
    google_event_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Google Event ID: {self.google_event_id} for Meeting: {self.meeting.subject}'

    class Meta:
        verbose_name = 'Calendar Event'
        verbose_name_plural = 'Calendar Events'
