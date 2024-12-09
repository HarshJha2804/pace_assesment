from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel

from pace_project.core.managers import GenericDocumentManager
from pace_project.core.models.core_models import DocumentTemplate
from pace_project.meetcom.models import CommunicationType
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from pace_project.utils.validators import file_size_validator

User = get_user_model()


class GenericRemark(TimeStampedModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    remark = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='remarks')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Remark by {self.created_by} on {self.content_object}: {self.remark[:50]}'

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = 'Remark'
        verbose_name_plural = 'Remarks'


class GenericFollowUp(TimeStampedModel):
    """
    A generic follow-up model to track follow-up actions for different entities.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    follow_up_date = models.DateField()
    follow_up_time = models.TimeField(null=True, blank=True)
    follow_up_note = models.TextField(null=True, blank=True)
    contact_method = models.ForeignKey(
        CommunicationType, on_delete=models.SET_NULL, related_name="follow_ups", null=True, blank=True
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_follow_ups'
    )
    is_completed = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='follow_ups'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Follow-up for {self.content_object} on {self.follow_up_date}"

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-follow_up_date', '-follow_up_time']
        verbose_name = 'Follow-up'
        verbose_name_plural = 'Follow-ups'


class GenericDocument(TimeStampedModel):
    """
    A generic document model to store documents with its type of all type entities.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    document_type = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True, related_name='documents')
    file = models.FileField(
        _("Document File"), upload_to='documents',
        validators=[file_size_validator(10)]
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents'
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))

    objects = GenericDocumentManager()

    class Meta:
        ordering = ['-created']
        unique_together = ('content_type', 'object_id', 'document_type', 'is_active')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return f'{self.document_type} - {self.content_object}'

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    @property
    def get_document_url(self):
        if self.file:
            return self.file.url
        else:
            return None


class Thread(TimeStampedModel):
    """Represents a thread of messages for Generic."""

    topic = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='threads')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.topic

    def soft_delete(self):
        """Soft delete the message."""
        self.is_active = False
        self.save()


class Message(TimeStampedModel):
    """Stores individual messages in a thread."""
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content = models.TextField()
    attachment = models.FileField(
        upload_to='message_attachments/',
        help_text=_("Attach files if necessary."),
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.thread

    def soft_delete(self):
        """Soft delete the message."""
        self.is_active = False
        self.save()

