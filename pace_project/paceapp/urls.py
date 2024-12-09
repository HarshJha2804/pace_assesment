from django.contrib.auth.decorators import login_required
from django.urls import path

import pace_project.paceapp.data_management_views
from pace_project.core.views import RegionalMarketingTargetsListView, ComplianceApplicationListView, \
    PremiumPartnerListView, ApplicationListView, RMApplicationListView, ApplicationManagerApplicationListView, \
    UniversityApplicationsListView, AssignApplicationManagerApplicationListView, AMApplicationDetailView, \
    RegionalMarketingHeadApplicationListView
from pace_project.paceapp import views
from pace_project.paceapp.ajax import get_campuses, get_board_or_state, get_other_countries, ajax_get_universities, \
    ajax_get_stream_or_campus, ajax_get_substream, ajax_get_streams, ajax_get_university_intakes
from pace_project.paceapp.api.views import CourseRecommendAPIView, BoardsByCountryAPIView, StatesByCountryAPIView, \
    SubStreamsByStreamAPIView, FilterCourseAPIView, CourseRequirementBoardListView, CourseFilterListView, \
    UniversityIntakeFilterListView, UniversityIntakeAPIView, StreamByLevelAPIView

from pace_project.paceapp.application_views import ApplyApplicationView, UpdateApplicationStatusView, \
    UpdateComplianceApplicationStatusView, UpdateApplicationManagerApplicationStatusView, chat_with_partner_view
from pace_project.paceapp.dashboard_views import RHMDashboardView, AssessmentOfficerDashboardView, AMDashboardView, \
    INODashboardView, CMPODashboardView, DataManagementOfficerDashboard, SuperAdminDashboardView, \
    PartnerOnBoardingOfficerDashboard, ProjectWiseDashboardView, VicePresidentDashboard
from pace_project.paceapp.views import HomeView, add_course_requirements_view, \
    discover_assessment_view, discover_pg_assessment_view, add_pg_course_requirements_view, \
    save_discovered_assessments_view, \
    DiscoveredASResultView, UploadStudentDocumentView, notification_redirect_view, account_signup_url_redirect_view, \
    notification_details_view, AORequestedAssessmentListView
from pace_project.paceapp.data_management_views import (
    AddCountryView, CountryUpdateView, AddUniversityGapView, CountryDeleteView,
    UpdateUniBoardGapView, UniBoardGapDeleteView, UniversityDetailView, AddUniversityStateMappingView,
    UBSSMappingUpdateView, UniversityStateMappingDeleteView, CourseListView, AddCourseView, CourseDetailView,
    CourseUpdateView, CourseEntryCriteriaUpdateView, CourseEntryCriteriaDeleteView, PGEntryCriteriaUpdateView,
    PGEntryCriteriaDeleteView, EnglishTestUpdateView, EnglishTestDeleteView, BoardCreateView, BoardUpdateView,
    BoardListView, BoardDeleteView, StateCreateView, StateListView, StateUpdateView, StateDeleteView, CampusListView,
    CampusCreateView, CampusUpdateView, CampusDeleteView, StreamListView, StreamCreateView, StreamDetailView,
    StreamUpdateView, StreamDeleteView, SubStreamCreateView, SubStreamListView, SubStreamUpdateView,
    SubStreamDeleteView, LevelListView, LevelCreateView, LevelDetailView, LevelUpdateView, LevelDeleteView,
    YearListView,
    YearUpdateView, YearCreateView, YearDeleteView, PartnerListView, PartnerCreateView, PartnerUpdateView,
    PartnerDeleteView, PartnerDetailView, StudentListView, StudentCreateView, StudentUpdateView, StudentDeleteView,
    PartnerBranchUpdateView, PartnerBranchDeleteView, AssessmentDiscoveryListView, StudentDetailView,
    student_academic_update_view, IntakeCreateView, IntakeListView, IntakeUpdateView, IntakeDeleteView,
    save_partner_contact_view, PartnerContactUpdateView, PartnerContactDeleteView,
    RegionCreateView, RegionListView, RegionUpdateView, RegionDeleteView, UniversityIntakeCreateView,
    UniversityIntakeUpdateView, UniversityIntakeDeleteView,
    UniversityIntakeListView, AssessmentListView, ApplicationAcceptingFromCountriesDetailView, ActiveCountryListView,
    ActiveCourseListView, AMStudentListView, AssessmentOfficerStudentListView, AMStudentUpdateView, AMStudentDeleteView,
    ASFStudentUpdateView, ASFStudentDeleteView, OnboardingPartnerCreateView, OnboardingPartnerListView,
    OnBoardedPartnerUpdateView, OnboardingPartnerDeleteView, OnboardingPartnerDetailView, DailyProgressReportCreateView,
    DailyProgressReportListView, DailyReportUpdateView
)

app_name = "paceapp"
urlpatterns = [
    path("accounts/signup/", account_signup_url_redirect_view, name="allauth_signup_url_redirect"),
    path("", login_required(HomeView.as_view()), name="home"),
    path('notification/<int:pk>/', login_required(notification_redirect_view), name="notification_redirect"),
    path("notification/<int:pk>/detail/", login_required(notification_details_view), name="notification_detail"),
]

urlpatterns += [
    path('universities/', login_required(pace_project.paceapp.data_management_views.UniversityListView.as_view()),
         name='university_list'),
    path('university/add/', login_required(pace_project.paceapp.data_management_views.UniversityCreateView.as_view()),
         name='add_university'),
    path('university/<int:pk>/add/gap/', login_required(AddUniversityGapView.as_view()), name='add_university_gap'),
    path('university/<int:pk>/', login_required(UniversityDetailView.as_view()), name='university_detail'),
    path('application-accepting/from-countries/<int:pk>',
         login_required(ApplicationAcceptingFromCountriesDetailView.as_view()),
         name='application_accept_country_detail'),
    path('universities/<int:pk>/update/', pace_project.paceapp.data_management_views.UniversityUpdateView.as_view(),
         name='update_university'),
    path(
        'university/gap/<int:pk>/update/', login_required(UpdateUniBoardGapView.as_view()),
        name='update_university_gap'
    ),
    path(
        'university/gap/<int:pk>/delete/',
        login_required(UniBoardGapDeleteView.as_view()),
        name='delete_university_gap'
    ),

    path('universities/<int:pk>/delete/', views.UniversityDeleteView.as_view(), name='delete_university'),
    path('university/<int:university_id>/applications/', UniversityApplicationsListView.as_view(),
         name='university_applications'),

]
urlpatterns += [
    path(
        'countries/', login_required(pace_project.paceapp.data_management_views.CountryListView.as_view()),
        name='country_list'
    ),
    path('country/add/', login_required(AddCountryView.as_view()), name='add_country'),
    path('country/<int:pk>/edit/', login_required(CountryUpdateView.as_view()), name='update_country'),
    path('country/<int:pk>/delete/', login_required(CountryDeleteView.as_view()), name='delete_country'),
]
urlpatterns += [
    path('university/<int:pk>/add/states/', login_required(AddUniversityStateMappingView.as_view()),
         name='add_university_state'),
    path(
        'university/state-mapping/<int:pk>/delete/', login_required(UniversityStateMappingDeleteView.as_view()),
        name='delete_university_state_mapping'
    ),
    path(
        'univeristy/bss-mapping/<int:pk>/edit/', login_required(UBSSMappingUpdateView.as_view()),
        name='update_university_bss_mapping'
    )
]

urlpatterns += [
    path('courses/', login_required(CourseListView.as_view()), name="course_list"),
    path('add/course/', login_required(AddCourseView.as_view()), name="add_course"),
    path(
        'course/<int:pk>/add/requirements/',
        login_required(add_course_requirements_view),
        name="add_course_requirements"
    ),
    path(
        'course/<int:pk>/add/pg/requirements/',
        login_required(add_pg_course_requirements_view),
        name="add_pg_course_requirements"
    ),
    path('course/<int:pk>/', login_required(CourseDetailView.as_view()), name="course_detail"),
    path('course/<int:pk>/edit/', login_required(CourseUpdateView.as_view()), name="update_course"),
    path(
        'course/entry-criteria/<int:pk>/edit/',
        login_required(CourseEntryCriteriaUpdateView.as_view()),
        name="update_entry_criteria"
    ),
    path(
        'course/entery-criteria/<int:pk>/delete/',
        login_required(CourseEntryCriteriaDeleteView.as_view()),
        name="delete_entry_criteria"
    )
]

urlpatterns += [
    path('english-test/<int:pk>/update/', login_required(EnglishTestUpdateView.as_view()), name="update_english_test"),
    path('english-test/<int:pk>/delete/', login_required(EnglishTestDeleteView.as_view()), name="delete_english_test"),
    path(
        'entry-criteria/pg/<int:pk>/update/',
        login_required(PGEntryCriteriaUpdateView.as_view()),
        name="update_pg_entry_criteria"
    ),
    path(
        'entry-criteria/pg/<int:pk>/delete/',
        login_required(PGEntryCriteriaDeleteView.as_view()),
        name="delete_pg_entry_criteria"
    ),
]

urlpatterns += [
    path("board/add/", login_required(BoardCreateView.as_view()), name="add_board"),
    path("board/<int:pk>/update/", login_required(BoardUpdateView.as_view()), name="update_board"),
    path("boards/", login_required(BoardListView.as_view()), name="board_list"),
    path("board/<int:pk>/delete/", login_required(BoardDeleteView.as_view()), name="delete_board"),
]
urlpatterns += [
    path("state/add/", login_required(StateCreateView.as_view()), name="add_state"),
    path("state/<int:pk>/update/", login_required(StateUpdateView.as_view()), name="update_state"),
    path("state/<int:pk>/delete/", login_required(StateDeleteView.as_view()), name="delete_state"),
    path("states/", login_required(StateListView.as_view()), name="state_list"),
]

urlpatterns += [
    path("region/add/", login_required(RegionCreateView.as_view()), name="add_region"),
    path("regions/", login_required(RegionListView.as_view()), name="region_list"),
    path("region/<int:pk>/update/", login_required(RegionUpdateView.as_view()), name="update_region"),
    path("region/<int:pk>/delete/", login_required(RegionDeleteView.as_view()), name="delete_region"),

]

urlpatterns += [
    path("campus/add/", login_required(CampusCreateView.as_view()), name="add_campus"),
    path("campus/<int:pk>/update/", login_required(CampusUpdateView.as_view()), name="update_campus"),
    path("campus/<int:pk>/delete/", login_required(CampusDeleteView.as_view()), name="delete_campus"),
    path("campuses/", login_required(CampusListView.as_view()), name="campus_list"),
]
urlpatterns += [
    path("stream/add/", login_required(StreamCreateView.as_view()), name="add_stream"),
    path("stream/<int:pk>/", login_required(StreamDetailView.as_view()), name="stream_detail"),
    path("stream/<int:pk>/edit/", login_required(StreamUpdateView.as_view()), name="update_stream"),
    path("stream/<int:pk>/delete/", login_required(StreamDeleteView.as_view()), name="delete_stream"),
    path("streams/", login_required(StreamListView.as_view()), name="stream_list"),
]

urlpatterns += [
    path('sub-stream/add/', login_required(SubStreamCreateView.as_view()), name="add_sub_stream"),
    path('sub-stream/<int:pk>/edit/', login_required(SubStreamUpdateView.as_view()), name="update_sub_stream"),
    path('sub-stream/<int:pk>/delete/', login_required(SubStreamDeleteView.as_view()), name="delete_sub_stream"),
    path('sub-streams/', login_required(SubStreamListView.as_view()), name="sub_stream_list"),
]

urlpatterns += [
    path('levels/', login_required(LevelListView.as_view()), name='level_list'),
    path('level/add/', login_required(LevelCreateView.as_view()), name='add_level'),
    path('level/<int:pk>/', login_required(LevelDetailView.as_view()), name='level_detail'),
    path('level/<int:pk>/edit/', login_required(LevelUpdateView.as_view()), name='update_level'),
    path('level/<int:pk>/delete/', login_required(LevelDeleteView.as_view()), name='delete_level'),
]

urlpatterns += [
    path('years/', login_required(YearListView.as_view()), name='year_list'),
    path('year/add/', login_required(YearCreateView.as_view()), name='add_year'),
    path('year/<int:pk>/edit/', login_required(YearUpdateView.as_view()), name='update_year'),
    path('year/<int:pk>/delete/', login_required(YearDeleteView.as_view()), name='delete_year'),
]
urlpatterns += [
    path('intakes/', login_required(IntakeListView.as_view()), name='intake_list'),
    path('intake/add/', login_required(IntakeCreateView.as_view()), name='add_intake'),
    path('intake/<int:pk>/edit/', login_required(IntakeUpdateView.as_view()), name='update_intake'),
    path('intake/<int:pk>/delete/', login_required(IntakeDeleteView.as_view()), name='delete_intake'),

]

urlpatterns += [
    path('university/intakes/', login_required(UniversityIntakeListView.as_view()),
         name='university_intake_list'),
    path('university/intake/add/', login_required(UniversityIntakeCreateView.as_view()),
         name='add_university_intake'),
    path('university/intake/<int:pk>/edit/', login_required(UniversityIntakeUpdateView.as_view()),
         name='update_university_intake'),
    path('university/intake/<int:pk>/delete/', login_required(UniversityIntakeDeleteView.as_view()),
         name='delete_university_intake'),

]

urlpatterns += [
    path('partners/', login_required(PartnerListView.as_view()), name='partner_list'),
    path('partner/add/', login_required(PartnerCreateView.as_view()), name='add_partner'),
    path('partner/<int:pk>/', login_required(PartnerDetailView.as_view()), name='partner_detail'),
    path('partner/<int:pk>/update/', login_required(PartnerUpdateView.as_view()), name='update_partner'),
    path('partner/<int:pk>/delete/', login_required(PartnerDeleteView.as_view()), name='delete_partner'),

    path(
        'partner/branch/<int:pk>/edit/',
        login_required(PartnerBranchUpdateView.as_view()),
        name='update_partner_branch'
    ),
    path(
        'partner/branch/<int:pk>/delete/',
        login_required(PartnerBranchDeleteView.as_view()),
        name='delete_partner_branch'
    ),
    path(
        'partner/<int:pk>/contact/save/',
        login_required(save_partner_contact_view), name='save_partner_contact'
    ),
    path(
        'partner/<int:pk>/contact/edit/',
        login_required(PartnerContactUpdateView.as_view()), name='update_partner_contact'
    ),
    path(
        'partner/<int:pk>/contact/delete/',
        login_required(PartnerContactDeleteView.as_view()),
        name='delete_partner_contact'
    ),
]

urlpatterns += [
    path('students/', login_required(StudentListView.as_view()), name='student_list'),
    path('student/add/', login_required(StudentCreateView.as_view()), name='add_student'),
    path('student/<int:pk>/', login_required(StudentDetailView.as_view()), name='student_detail'),
    path('student/<int:pk>/edit/', login_required(StudentUpdateView.as_view()), name='update_student'),
    path('student/<int:pk>/delete/', login_required(StudentDeleteView.as_view()), name='delete_student'),
    path('am/students/', login_required(AMStudentListView.as_view()), name='am_student_list'),
    path('asf/students/', login_required(AssessmentOfficerStudentListView.as_view()), name='asf_student_list'),
    path('am/student/<int:pk>/edit/', login_required(AMStudentUpdateView.as_view()), name='am_update_student'),
    path('am/student/<int:pk>/delete/', login_required(AMStudentDeleteView.as_view()), name='am_delete_student'),
    path('asf/student/<int:pk>/edit/', login_required(ASFStudentUpdateView.as_view()), name='asf_update_student'),
    path('asf/student/<int:pk>/delete/', login_required(ASFStudentDeleteView.as_view()), name='asf_delete_student'),

    # Student Academics
    path(
        'student/<int:pk>/acadmic/edit/', login_required(student_academic_update_view),
        name='update_student_academic'
    ),
    path(
        "student/<int:pk>/upload/document/", login_required(UploadStudentDocumentView.as_view()),
        name="upload_student_document"
    )
]

urlpatterns += [
    path(
        'assessment/discoveries/', login_required(AssessmentDiscoveryListView.as_view()),
        name='assessment_discovery_list'
    ),
]

urlpatterns += [
    path(
        'student/<int:pk>/apply/application/', login_required(ApplyApplicationView.as_view()), name='apply_application'
    ),
]

urlpatterns += [
    path("dashboard/super-admin/", login_required(SuperAdminDashboardView.as_view()), name="super_admin_dashboard"),
    path("project/wise/dashboard/", login_required(ProjectWiseDashboardView.as_view()), name="project_wise_dashboard"),
    path(
        'dashboard/regional-marketing-head/', login_required(RHMDashboardView.as_view()),
        name='dashboard_regional_marketing_head'
    ),

    path('dashboard/interview-officer/', login_required(INODashboardView.as_view()),
         name='dashboard_interview_officer'),

]

urlpatterns += [
    path('discover/assessment/', discover_assessment_view, name='discover_assessment'),
    path('discover/pg/assessment/', discover_pg_assessment_view, name='discover_pg_assessment'),
    path('discovered/assessment/save/', login_required(save_discovered_assessments_view), name='save_assessment'),
    path('assessment-result/', login_required(DiscoveredASResultView.as_view()), name='discover_assessment_result'),
    path('student/<str:pk>/save/assessment/', login_required(views.save_assessments_view), name='assessment_save'),
    path('student/<int:pk>/mark/reject/',
         login_required(views.mark_student_status_reject_view), name='reject_student'),
    path('application/<str:pk>/', login_required(views.save_application_view), name='application_save'),

    path("application/<int:pk>/chat/with/partner/", login_required(chat_with_partner_view), name="chat_with_partner"),
]

urlpatterns += [
    # Ajax URLs
    path('ajax/get-campus/', login_required(get_campuses), name='ajax_get_campus'),
    path('ajax/get/board/or/state/', login_required(get_board_or_state), name='ajax_get_board_or_state'),
    path('ajax/get-other-countries/', login_required(get_other_countries), name='ajax_get_other_countries'),
    path('ajax/get-universities/', login_required(ajax_get_universities), name='ajax_get_universities'),
    path(
        'ajax/get-university-intakes/', login_required(ajax_get_university_intakes), name='ajax_get_university_intakes'
    ),

    path('ajax/get/streams/and/campus/', login_required(ajax_get_stream_or_campus), name='ajax_get_or_streams_camp'),
    path('ajax/get/streams/', login_required(ajax_get_streams), name='ajax_get_streams'),
    path('ajax/get/substream/', login_required(ajax_get_substream), name='ajax_get_substream'),
]

# Assessment Officer Dashboard

urlpatterns += [
    path('dashboard/assessment-officer/', login_required(AssessmentOfficerDashboardView.as_view()),
         name='assessment_dashboard'),
    path('assessments/', login_required(AssessmentListView.as_view()), name='assessment_list'),
    path('dashboard/data-management-officer/', login_required(DataManagementOfficerDashboard.as_view()),
         name='data_management_officer'),
    path('active-country/', login_required(ActiveCountryListView.as_view()), name='active_country_list'),
    path('active-courses/', login_required(ActiveCourseListView.as_view()), name='active_course_list'),
    path('assessments/request/', login_required(AORequestedAssessmentListView.as_view()),
         name='requested_assessment_list'),

]

# compliance Officer Dashboard

urlpatterns += [

    path('dashboard/compliance-officer/', login_required(CMPODashboardView.as_view()),
         name='dashboard_compliance_officer'),

    path('compliance/applications/', login_required(ComplianceApplicationListView.as_view()),
         name='compliance_application_list'),
    path('compliance-application/<int:pk>/update/', login_required(UpdateComplianceApplicationStatusView.as_view()),
         name='update_compliance_application'),

]

# Regional Marketing Head  Tabs

urlpatterns += [
    path('targets/', login_required(RegionalMarketingTargetsListView.as_view()),
         name='target_list'),
    path('premium-partner/', login_required(PremiumPartnerListView.as_view()),
         name='premium_partner_list'),
    path('application/', login_required(RMApplicationListView.as_view()), name='rm_application_list'),
    path('all-application/', login_required(RegionalMarketingHeadApplicationListView.as_view()),
         name='regional_application_list'),
    path('add/report/', login_required(DailyProgressReportCreateView.as_view()), name='daily_report_create'),
    path('reports/', login_required(DailyProgressReportListView.as_view()), name='daily_report_list'),
    path('reports/<int:pk>/update/', login_required(DailyReportUpdateView.as_view()), name='daily_report_update'),
]

# Application Manager Dashboard

urlpatterns += [

    path('dashboard/application-manager/', login_required(AMDashboardView.as_view()),
         name='dashboard_application_manager'),

    path('application-manager/applications/', login_required(ApplicationManagerApplicationListView.as_view()),
         name='application_manager_application_list'),
    path('application-manager/application/<int:pk>/update/',
         login_required(UpdateApplicationManagerApplicationStatusView.as_view()),
         name='update_application_manager_application'),

    path('assign-application-manager/applications/',
         login_required(AssignApplicationManagerApplicationListView.as_view()),
         name='assign_application_manager_application_list'),
    path('am/application/<int:pk>/detail/', login_required(AMApplicationDetailView.as_view()),
         name="am_application_detail"),

]
urlpatterns += [

    path('dashboard/partner-onboarding-officer/', login_required(PartnerOnBoardingOfficerDashboard.as_view()),
         name='dashboard_partner_onboarding_officer'),

]

urlpatterns += [
    path('partner/onboarding', login_required(OnboardingPartnerCreateView.as_view()), name='partner_onboarding'),
    path('onboarded/partner/', login_required(OnboardingPartnerListView.as_view()), name='onboarded_partner'),
    path('onboarded/partner/<int:pk>/update/', login_required(OnBoardedPartnerUpdateView.as_view()),
         name='onboarded_partner_update'),
    path('onboarded/partner/<int:pk>/delete/', login_required(OnboardingPartnerDeleteView.as_view()),
         name='onboarded_partner_delete'),
    path('onboarded/partner/<int:pk>/detail/', login_required(OnboardingPartnerDetailView.as_view()),
         name='onboarded_partner_detail'),
]

# Vice President URLS
urlpatterns += [
    path('dashboard/vice-president/', login_required(VicePresidentDashboard.as_view()),
         name='dashboard_vice_president'),
]

urlpatterns += [
    # APIs URLs
    path('api/recommend/course/', CourseRecommendAPIView.as_view(), name='api_recommend_course'),
    path('api/boards-by-country/', BoardsByCountryAPIView.as_view(), name='api_boards_by_country'),
    path('api/states-by-country/', StatesByCountryAPIView.as_view(), name='api_states_by_country'),
    path('api/streams-by-level/', StreamByLevelAPIView.as_view(), name='api_streams_by_level'),
    path('api/substreams-by-stream/', SubStreamsByStreamAPIView.as_view(), name='api_substreams_by_stream'),
    path(
        'api/courses/<int:course_id>/boards/', CourseRequirementBoardListView.as_view(),
        name='api_course_requirement_boards'
    ),
    path('api/filter/course/', FilterCourseAPIView.as_view(), name='api_filter_course'),
    path(
        "api/university/<int:university_id>/intakes/", UniversityIntakeAPIView.as_view(),
        name="api_university_intake"
    ),

    path('api/courses/', CourseFilterListView.as_view(), name='course_list_filter'),
    path('api/intakes/<int:university_id>/', UniversityIntakeFilterListView.as_view(), name='university_intake_list'),
]
