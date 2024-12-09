import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async

from pace_project.core.models.application_models import Application
from pace_project.paceapp.models import AssessmentDiscovery
from pace_project.users.models import Student, Partner


class CEODashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "dashboard"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_update(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))


@receiver(post_save, sender=Student)
@receiver(post_save, sender=Application)
@receiver(post_save, sender=AssessmentDiscovery)
def notify_ceo_dashboard(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    data = {
        "student_count": Student.objects.filter(is_active=True).count(),
        "application_count": Application.objects.filter(is_active=True).count(),
        "assessment_count": AssessmentDiscovery.objects.filter(is_active=True).count(),
        "partner_count": Partner.objects.filter(is_active=True).count(),
    }
    async_to_sync(channel_layer.group_send)(
        "dashboard",
        {
            'type': 'send_update',
            'data': data,
        }
    )
