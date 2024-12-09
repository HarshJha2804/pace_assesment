from django.db import models
from django.utils import timezone


class MeetingManager(models.Manager):
    def upcoming(self):
        return self.filter(scheduled_date__gte=timezone.now()).order_by('scheduled_date')
