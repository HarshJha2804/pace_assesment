from django.urls import path
from django.contrib.auth.decorators import login_required

from pace_project.paceapp.data_management_views import PartnerAccountManagerApplicationListView
from pace_project.partner import views
from pace_project.partner.ajax import ajax_state_by_country_view
from pace_project.partner.api.views import DirectApplyCourseAPIView
from pace_project.partner.views import PartnerDashboardView, PartnerStudentListView, \
    UploadPartnerDocumentView, PartnerAgreementListView, PartnerStudentDetailView, \
    CommissionStructureListView, PartnerApplicationList, ApplicationApplyView, RequestAssessmentView, \
    RequestedAssessmentListView, redirect_view, PartnerAssessmentListView, \
    PartnerCommissionCreateView, PartnerCommissionUpdateView, PartnerUniversityListView, SetPartnerCommissionCreateView, \
    PartnerCountryDashboard, AccountManagerPartnerListView, PartnerAccountManagerStudentListView
from pace_project.partner.application_views import apply_application_from_university_view, PartnerStudentCreateView, \
    PartnerStudentUpdateView, create_student_application_view, PartnerUploadStudentDocumentView, ApplicationDetailView, \
    chat_with_team_view

app_name = "partner"
urlpatterns = [
    path("", login_required(redirect_view), name="redirect_view"),
    path('dashboard/', login_required(PartnerDashboardView.as_view()), name="dashboard_partner"),
    path('countrydashboard/<int:pk>/', login_required(PartnerCountryDashboard.as_view()),
         name="country_dashboard_partner"),
    path("register/", views.PartnerRegisterView.as_view(), name="register"),
    path('upload/agreement', login_required(UploadPartnerDocumentView.as_view()), name='upload_docs'),
    path('agreements/', login_required(PartnerAgreementListView.as_view()), name='docs'),
]
urlpatterns += [
    path(
        "commission-structure/", login_required(CommissionStructureListView.as_view()),
        name='partner_commission_list'
    ),
    path(
        "set/commission/<int:partner_id>/", login_required(PartnerCommissionCreateView.as_view()),
        name='set_commission'
    ),
    path(
        "commission/<int:partner_id>/update/", login_required(PartnerCommissionUpdateView.as_view()),
        name='partner_commission_update'),
]

urlpatterns += [
    path('students/', login_required(PartnerStudentListView.as_view()), name='list_student'),
    path('student/add/', login_required(PartnerStudentCreateView.as_view()), name='create_student'),
    path('student/<int:pk>/update', login_required(PartnerStudentUpdateView.as_view()), name='update_student'),
    path('student/<int:pk>/', login_required(PartnerStudentDetailView.as_view()), name='partner_student_detail'),
    path("student/<int:pk>/upload/document/", login_required(PartnerUploadStudentDocumentView.as_view()),
         name="partner_upload_student_document"),
]

urlpatterns += [
    path("applications/", login_required(PartnerApplicationList.as_view()), name="application_list"),
    path("application/<int:pk>/", login_required(ApplicationDetailView.as_view()), name="application_detail"),
    path("application/<int:pk>/chat/with/team/", login_required(chat_with_team_view), name="chat_with_team"),
    path("apply/<int:pk>/application/", login_required(ApplicationApplyView.as_view()), name="application_apply"),
    path("student/<int:pk>/apply/", login_required(create_student_application_view), name="create_student_application"),
]

urlpatterns += [
    path("universities/", login_required(PartnerUniversityListView.as_view()), name="university_list"),
    path(
        "university/direct-apply/", login_required(apply_application_from_university_view),
        name="university_application_apply"
    )
]

urlpatterns += [
    path(
        "student/<int:pk>/assessment/requested/", login_required(RequestAssessmentView.as_view()),
        name="request_assessment"
    ),
    path(
        "student/assessment/", login_required(PartnerAssessmentListView.as_view()), name='partner_assessment_list'
    ),
    path("request/assessment", login_required(RequestedAssessmentListView.as_view()),
         name='partner_requested_assessment'),
]

urlpatterns += [
    # API URLs
    path('api/direct/apply/courses/', DirectApplyCourseAPIView.as_view(), name='api_direct_apply_course'),
    path("ajax/states/", ajax_state_by_country_view, name="ajax_state_by_country"),
]

# partner commission
urlpatterns += [
    path('set/commission/', login_required(SetPartnerCommissionCreateView.as_view()), name='set_commission_up'),
]

# Partner Account Dashboard
urlpatterns += [
    path('account-manager/partners', login_required(AccountManagerPartnerListView.as_view()),
         name='account_manager_partners_list'),
    path('account-manager/applications/', login_required(PartnerAccountManagerApplicationListView.as_view()),
         name='account_manager_applications_list'),
    path('account-manager/students/', login_required(PartnerAccountManagerStudentListView.as_view()),
         name='account_manager_students_list'),
]
