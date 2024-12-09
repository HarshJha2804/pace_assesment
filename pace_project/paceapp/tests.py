from asgiref.sync import sync_to_async
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from pace_project.paceapp.consumers import CEODashboardConsumer
from pace_project.paceapp.models import Country
from pace_project.users.models import Student, Partner


class CEODashboardConsumerTest(TestCase):
    async def test_ceo_dashboard_update(self):
        # Connect to the WebSocket
        communicator = WebsocketCommunicator(CEODashboardConsumer.as_asgi(), "/ws/dashboard/")
        connected, sub_protocol = await communicator.connect()
        self.assertTrue(connected)

        country = await sync_to_async(Country.objects.create)(country_name="United Kingdom")
        partner = await sync_to_async(Partner.objects.create)(company_name="Infinite Group", country=country)

        # Create student objects
        await sync_to_async(Student.objects.create)(first_name="Foo Barr", partner=partner)
        await sync_to_async(Student.objects.create)(first_name="Elon Musk", partner=partner)

        # Check that the WebSocket received the correct data
        response = await communicator.receive_json_from()
        self.assertEqual(response['student_count'], 1)

        # Disconnect the WebSocket
        await communicator.disconnect()
