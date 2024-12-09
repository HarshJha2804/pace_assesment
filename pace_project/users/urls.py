from django.contrib.auth.decorators import login_required
from django.urls import path

from .ajax import mark_all_as_read_ajax, get_notifications_ajax
from .api.views import EmpowerEDUQueryAPIView
from .data_management_views import EmployeeListView, UserListView, AssignRegionView, RMListView, SetRMTargetView, \
    ApplicationManagerListView, ApplicationManagerUpdateView, EmployeeUpdateView, UserUpdateView, \
    SetRMUniversityIntakeView

from .views import user_detail_view, PartnerFollowUpView, mark_partner_not_interested_view, \
    mark_partner_interested_view, add_ug_student_academic_view, add_pg_student_academic_view, upload_logo_view

from .views import user_redirect_view
from .views import user_update_view
from .data_management_views import RoleCreateView, RoleListView, RoleUpdateView, RoleDeleteView

from pace_project.users.data_management_views import UserSignupView, EmployeeSignupView, EmployeeDetailView

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path('upload_logo/', view=upload_logo_view, name='upload_logo_view'),


]

urlpatterns += [
    # Roles
    path("roles/", login_required(RoleListView.as_view()), name="role_list"),
    path('role/add/', login_required(RoleCreateView.as_view()), name='role_add'),
    path("role/<int:pk>/update/", login_required(RoleUpdateView.as_view()), name="update_role"),
    path("role/<int:pk>/delete/", login_required(RoleDeleteView.as_view()), name="delete_role"),

]

urlpatterns += [
    # Users
    path('users/', login_required(UserListView.as_view()), name='user_list'),
    path('add/user/', login_required(UserSignupView.as_view()), name='add_user'),
    path('users/<int:pk>/update/', login_required(UserUpdateView.as_view()), name='update_user'),

]

urlpatterns += [
    # Employees
    path('teams/', login_required(EmployeeListView.as_view()), name='employee_list'),
    path('add/team/member/', login_required(EmployeeSignupView.as_view()), name='add_employee_list'),
    path("team/member/<int:pk>/", login_required(EmployeeDetailView.as_view()), name="employee_detail"),
    path("team/member/<int:pk>/assign/region/", login_required(AssignRegionView.as_view()), name="assign_region"),

    # RMHs
    path("team/reginoal-marketing-heads/", login_required(RMListView.as_view()), name="rm_list"),
    path("rm/<int:pk>/set/target/", login_required(SetRMTargetView.as_view()), name="set_rm_target"),
    path("rm/<int:pk>/set/university/intake/", login_required(SetRMUniversityIntakeView.as_view()),
         name="set_rm_university_intake"),

    # application manager
    path("team/application-managers/", login_required(ApplicationManagerListView.as_view()),
         name="application_manager_list"),
    path("team/application-managers/<int:pk>/update/", login_required(ApplicationManagerUpdateView.as_view()),
         name="update_application_manager"),
    path("team/employee/<int:pk>/update/", login_required(EmployeeUpdateView.as_view()),
         name="update_employee")
]

urlpatterns += [
    path('partner/<int:pk>/set/follow-up/', login_required(PartnerFollowUpView.as_view()), name='set_partner_followup'),
    path(
        "partner/<int:pk>/mark/as/not/interseted/",
        login_required(mark_partner_not_interested_view), name="mark_partner_not_interested"
    ),
    path(
        "partner/<int:pk>/mark-interested/", login_required(mark_partner_interested_view),
        name="mark_partner_interested"
    ),
]

urlpatterns += [
    path(
        "student/<int:pk>/add/ug/academics/",
        login_required(add_ug_student_academic_view), name="add_ug_student_academic"
    ),
    path(
        "student/<int:pk>/add/pg/academics/",
        login_required(add_pg_student_academic_view), name="add_pg_student_academic"
    )
]
urlpatterns += [
    # Ajax URLs
    path(
        'notifications/mark-all-as-read/', login_required(mark_all_as_read_ajax),
        name="notification_mark_all_as_read"
    ),
    path(
        'notifications/api/read-and-unread/list/', login_required(get_notifications_ajax),
        name="notifications_read_and_unread_list"
    ),
]

urlpatterns += [
    path("api/empower-edu/query/", EmpowerEDUQueryAPIView.as_view(), name="empower_edu_query")
]
