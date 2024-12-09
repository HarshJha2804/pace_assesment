from django.contrib.auth.decorators import login_required
from django.urls import path
from pace_project.meetcom.views.meeting_views import MeetingListView, MeetingCreateView, MeetingUpdateView, \
    MeetingDeleteView, \
    MeetingDetailView, RMMeetingCreateView, RMMeetingListView, RMMeetingDeleteView, RMMeetingUpdateView, \
    RMMeetingDetailView, WebinarCreateView, WebinarListView

app_name = "meetcom"

urlpatterns = [

    path("meetings/", login_required(MeetingListView.as_view()),
         name="meeting_list"),
    path("meeting/add/", login_required(MeetingCreateView.as_view()),
         name="add_meeting"),
    path("meeting/<int:pk>/update/", login_required(MeetingUpdateView.as_view()),
         name="update_meeting"),
    path("meeting/<int:pk>/delete/", login_required(MeetingDeleteView.as_view()),
         name="delete_meeting"),
    path("meeting/<int:pk>/", login_required(MeetingDetailView.as_view()),
         name="meeting_detail"),
]

urlpatterns += [
    path("rm/meeting/add/", login_required(RMMeetingCreateView.as_view()), name="rm_meeting"),
    path("rm/meeting/", login_required(RMMeetingListView.as_view()), name="rm_meeting_list"),
    path("rm/meeting/<int:pk>/delete", login_required(RMMeetingDeleteView.as_view()), name="rm_meeting_list_delete"),
    path("rm/meeting/<int:pk>/update/", login_required(RMMeetingUpdateView.as_view()), name="rm_meeting_update"),
    path("rm/meeting/<int:pk>/detail/", login_required(RMMeetingDetailView.as_view()), name="rm_meeting_detail"),

]
urlpatterns += [
    path('add/webinar/', login_required(WebinarCreateView.as_view()), name='add_webinar'),
    path('webinar/list/', login_required(WebinarListView.as_view()), name='webinar_list'),
]
