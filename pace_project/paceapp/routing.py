from django.urls import path, re_path

from pace_project.paceapp import consumers

websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', consumers.CEODashboardConsumer.as_asgi()),
]
