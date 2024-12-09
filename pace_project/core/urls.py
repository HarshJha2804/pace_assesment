from django.urls import path
from django.contrib.auth.decorators import login_required
from pace_project.core.data_management_views import AddPartnerSupportDocumentCreateView, PartnerSupportDocumentListView, \
    PartnerSupportDocumentUpdateView, PartnerSupportDocumentDeleteView, AddCommissionStructureView, \
    CommissionStructureListView, CommissionStructureUpdateView, CommissionStructureDeleteView, \
    UniversityInterviewStatusListView, UniversityInterviewStatusCreateView, InterviewStatusListView, \
    InterviewStatusCreateView, InterviewStatusUpdateView, UpdatedNewsCreateView, NewsListView, ContactUsCreateView, \
    ContactUsListView, ContactUsReplyCreateView
from pace_project.core.interview_officer_views import INOApplicationListView
from pace_project.core.models.core_models import UpdateNews
from pace_project.core.views import DocumentTemplateListView, DocumentTemplateCreateView, DocumentTemplateUpdateView, \
    DocumentTemplateDeleteView, StatusTypeListView, StatusTypeCreateView, StatusTypeUpdateView, StatusTypeDeleteView, \
    CountrySpecificStatusListView, CountrySpecificStatusCreateView, CountrySpecificStatusUpdateView, \
    CountrySpecificStatusDeleteView, CountrySpecificStatusDetailView, CountrySpecificDocumentCreateView, \
    CountrySpecificDocumentListView, CountrySpecificDocumentUpdateView, CountrySpecificDocumentDeleteView, \
    CountrySpecificDocumentDetailView, StaffingRequirementListView, StaffingRequirementCreateView, \
    StaffingRequirementUpdateView, StaffingRequirementDeleteView, UniversityTargetListView, UniversityTargetCreateView, \
    UniversityTargetUpdateView, UniversityTargetDeleteView, ApplicationListView, RMTargetListView, RMTargetCreateView, \
    RMTargetUpdateView, RMTargetDeleteView, CountrySpecificLevelCreateView, CountrySpecificLevelListView, \
    CountrySpecificLevelUpdateView, CountrySpecificLevelDeleteView, CountrySpecificLevelDetailView, \
    ApplicationPendingFromIOAListView, ApplicationPendingFromAgentListView, ApplicationSubmittedView, \
    ApplicationDetailView, DynamicFieldListView, DynamicFieldCreateView, DynamicFieldUpdateView, DynamicFieldDeleteView, \
    CountrySpecificFieldCreateView, CountrySpecificFieldListView, CountrySpecificFieldUpdateView, \
    CountrySpecificFieldDeleteView, CountrySpecificFieldDetailView, ConditionCreateView, ConditionListView, \
    UpdateConditionView
from pace_project.paceapp.application_views import UpdateApplicationStatusView

app_name = "core"

urlpatterns = [
    # Partner Support Document URLs
    path(
        'add/partner-support/document/', login_required(AddPartnerSupportDocumentCreateView.as_view()),
        name='add_partner_support_document'
    ),
    path(
        'partner-support/documents/', login_required(PartnerSupportDocumentListView.as_view()),
        name='partner_support_document_list'
    ),
    path(
        'partner-support/document/<int:pk>/edit/', login_required(PartnerSupportDocumentUpdateView.as_view()),
        name='update_partner_support_document'
    ),
    path(
        'partner-support/document/<int:pk>/delete/', login_required(PartnerSupportDocumentDeleteView.as_view()),
        name='delete_partner_support_document'
    ),
]

# Document template URLs

urlpatterns += [
    path('document/templates/', login_required(DocumentTemplateListView.as_view()), name='document_template_list'),
    path('document/template/add/', login_required(DocumentTemplateCreateView.as_view()), name='add_document_template'),
    path('document/template/<int:pk>/edit/', login_required(DocumentTemplateUpdateView.as_view()),
         name='update_document_template'),
    path('document/template/<int:pk>/delete/', login_required(DocumentTemplateDeleteView.as_view()),
         name='delete_document_template'),
]

urlpatterns += [
    path('status/types/', login_required(StatusTypeListView.as_view()), name='status_type_list'),
    path('status/type/add/', login_required(StatusTypeCreateView.as_view()), name='add_status_type'),
    path('status/type/<int:pk>/edit/', login_required(StatusTypeUpdateView.as_view()),
         name='update_status_type'),
    path('status/type/<int:pk>/delete/', login_required(StatusTypeDeleteView.as_view()),
         name='delete_status_type'),
]

urlpatterns += [
    path(
        'country-specific/status/', login_required(CountrySpecificStatusListView.as_view()),
        name='country_specific_status_list'
    ),
    path(
        'country-specific/status/add/', login_required(CountrySpecificStatusCreateView.as_view()),
        name='add_country_specific_status'
    ),
    path(
        'country-specific/status/<int:pk>/edit/', login_required(CountrySpecificStatusUpdateView.as_view()),
        name='update_country_specific_status'
    ),
    path(
        'country-specific/status/<int:pk>/delete/', login_required(CountrySpecificStatusDeleteView.as_view()),
        name='delete_country_specific_status'
    ),

    path("country-specific/status/<int:pk>/", login_required(CountrySpecificStatusDetailView.as_view()),
         name="country_specific_status_detail"),
]

urlpatterns += [

    path(
        'country-specific/document/add/', login_required(CountrySpecificDocumentCreateView.as_view()),
        name='add_country_specific_document'
    ),
    path('country-specific/documents/', login_required(CountrySpecificDocumentListView.as_view()),
         name='country_specific_document_list'),

    path(
        'country-specific/document/<int:pk>/edit/', login_required(CountrySpecificDocumentUpdateView.as_view()),
        name='update_country_specific_document'
    ),

    path(
        'country-specific/document/<int:pk>/delete/', login_required(CountrySpecificDocumentDeleteView.as_view()),
        name='delete_country_specific_document'
    ),

    path(
        'country-specific/document/<int:pk>/detail/', login_required(CountrySpecificDocumentDetailView.as_view()),
        name='country_specific_document_detail'
    ),
]

urlpatterns += [
    path('team/requirements/', login_required(StaffingRequirementListView.as_view()),
         name='staffing_requirement_list'),
    path('staffing-requirement/add/', login_required(StaffingRequirementCreateView.as_view()),
         name='add_staffing_requirement'),
    path('staffing-requirement/<int:pk>/edit/', login_required(StaffingRequirementUpdateView.as_view()),
         name='update_staffing_requirement'),
    path('staffing-requirement/<int:pk>/delete/', login_required(StaffingRequirementDeleteView.as_view()),
         name='delete_staffing_requirement'),
]

urlpatterns += [
    path('university/targets/', login_required(UniversityTargetListView.as_view()),
         name='university_target_list'),
    path('university/target/add/', login_required(UniversityTargetCreateView.as_view()),
         name='add_university_target'),
    path('university/target/<int:pk>/edit/', login_required(UniversityTargetUpdateView.as_view()),
         name='update_university_target'),
    path('university/target/<int:pk>/delete/', login_required(UniversityTargetDeleteView.as_view()),
         name='delete_university_target'),

]

urlpatterns += [
    path('applications/', login_required(ApplicationListView.as_view()),
         name='application_list'),
    path('application/<int:pk>/update/', login_required(UpdateApplicationStatusView.as_view()),
         name='update_application'),

    path('pending-applications-from-ioa/', login_required(ApplicationPendingFromIOAListView.as_view()),
         name='applications_pending_from_ioa'),
    path('pending-applications-from-agent/', login_required(ApplicationPendingFromAgentListView.as_view()),
         name='applications_pending_from_agent'),
    path('application-submit/', login_required(ApplicationSubmittedView.as_view()), name='application_submit'),

]

urlpatterns += [
    path('rm/targets/', login_required(RMTargetListView.as_view()),
         name='rm_target_list'),
    path('rm/target/add/', login_required(RMTargetCreateView.as_view()),
         name='add_rm_target'),
    path('rm/target/<int:pk>/edit/', login_required(RMTargetUpdateView.as_view()),
         name='update_rm_target'),
    path('rm/target/<int:pk>/delete/', login_required(RMTargetDeleteView.as_view()),
         name='delete_rm_target'),
]

urlpatterns += [

    path('country-specific/level/add/', login_required(CountrySpecificLevelCreateView.as_view()),
         name='add_country_specific_level'),
    path('country-specific/levels/', login_required(CountrySpecificLevelListView.as_view()),
         name='country_specific_level_list'),
    path('country-specific/level/<int:pk>/edit/', login_required(CountrySpecificLevelUpdateView.as_view()),
         name='update_country_specific_level'),
    path('country-specific/level/<int:pk>/delete/', login_required(CountrySpecificLevelDeleteView.as_view()),
         name='delete_country_specific_level'),

    path('country-specific/level/<int:pk>/detail/', login_required(CountrySpecificLevelDetailView.as_view()),
         name='country_specific_level_detail'),
]

urlpatterns += [
    path("application/<int:pk>/", login_required(ApplicationDetailView.as_view()), name="application_detail"),
]

# Dynamic Field

urlpatterns += [
    path('dynamic-field/', login_required(DynamicFieldListView.as_view()), name='dynamic_field_list'),
    path('dynamic-field/add', login_required(DynamicFieldCreateView.as_view()), name='create_dynamic_field'),
    path('dynamic-field/<int:pk>/update', login_required(DynamicFieldUpdateView.as_view()),
         name='update_dynamic_field'),
    path('dynamic-field/<int:pk>/delete', login_required(DynamicFieldDeleteView.as_view()),
         name='dynamic_field_delete'),

]

urlpatterns += [
    path('country-specific/field/add/', login_required(CountrySpecificFieldCreateView.as_view()),
         name='add_country_specific_field'),
    path('country-specific/fields/', login_required(CountrySpecificFieldListView.as_view()),
         name='country_specific_field_list'),
    path('country-specific/field/<int:pk>/edit/', login_required(CountrySpecificFieldUpdateView.as_view()),
         name='update_country_specific_field'),
    path('country-specific/field/<int:pk>/delete/', login_required(CountrySpecificFieldDeleteView.as_view()),
         name='delete_country_specific_field'),
    path('country-specific/field/<int:pk>/detail/', login_required(CountrySpecificFieldDetailView.as_view()),
         name='country_specific_field_detail'),
]

urlpatterns += [
    path(
        "add/commission/structure/", login_required(AddCommissionStructureView.as_view()),
        name='add_commission_structure'
    ),
    path(
        "commission/structures/", login_required(CommissionStructureListView.as_view()),
        name='commission_structure_list'
    ),
    path(
        "commission/structure/<int:pk>/update/", login_required(CommissionStructureUpdateView.as_view()),
        name='update_commission_structure'
    ),
    path(
        "commission/structure/<int:pk>/delete/", login_required(CommissionStructureDeleteView.as_view()),
        name='delete_commission_structure'
    ),
]
urlpatterns += [
    # Interview Status Type URLs
    path(
        "interview/status/types/", login_required(InterviewStatusListView.as_view()),
        name="interview_status_type_list"
    ),
    path(
        "interview/status/type/add/", login_required(InterviewStatusCreateView.as_view()),
        name="add_interview_statu_type"
    ),
    path(
        "interview/status/<int:pk>/update/", login_required(InterviewStatusUpdateView.as_view()),
        name="update_interview_status_type"
    )
]
urlpatterns += [
    # University Interview status URLs
    path(
        "university/interview/status/types/", login_required(UniversityInterviewStatusListView.as_view()),
        name="university_interview_status_list"
    ),

    path(
        "add/university/interview-status/", login_required(UniversityInterviewStatusCreateView.as_view()),
        name='add_university_interview_status'
    ),
]

urlpatterns += [
    path("interview/applications/", login_required(INOApplicationListView.as_view()), name="interview_application_list")
]

urlpatterns += [

    path("add-condition/", login_required(ConditionCreateView.as_view()), name="add_condition"),
    path("conditions/", login_required(ConditionListView.as_view()), name="condition_list"),
    path("update-condition/<int:pk>/", login_required(UpdateConditionView.as_view()), name="update_condition"),
]
urlpatterns += [
    path('update/', login_required(UpdatedNewsCreateView.as_view()), name='update_news'),
    path('news/list/', login_required(NewsListView.as_view()), name='news_list'),
]
urlpatterns += [
    path('add/contact-us/', login_required(ContactUsCreateView.as_view()), name='contact_us'),
    path('contact-us/', login_required(ContactUsListView.as_view()), name='contact_us_list'),
    path('contact_us/reply/<int:contact_us_id>/', login_required(ContactUsReplyCreateView.as_view()),
         name='reply_view'),
]
