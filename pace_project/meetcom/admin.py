from django.contrib import admin

from pace_project.meetcom.models import Meeting, CommunicationType, Communication, CalendarEvent


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['subject', 'scheduled_date', 'status', 'created']
    list_filter = ['status']


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ['communication_type', 'subject', 'body', 'related_meeting', 'created_by', 'is_active']
    list_filter = ['subject']


@admin.register(CommunicationType)
class CommunicationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_filter = ['name']


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'google_event_id', 'is_active']
    list_filter = ['meeting']
