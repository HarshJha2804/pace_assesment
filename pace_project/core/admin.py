from django.contrib import admin

from pace_project.core.models.generic_models import GenericRemark, GenericFollowUp, GenericDocument, Thread, Message
from pace_project.core.models.target_models import UniversityTarget, RMTarget, RMUniversityIntake
from pace_project.core.models.requirement_models import StaffingRequirement
from pace_project.core.models.application_models import Application, ApplicationStatusLog, ApplicationRemark, \
    ApplicationAttribute, InterviewActivity, ApplicationAssignmentLog
from pace_project.core.models.core_models import DocumentTemplate, PartnerSupportDocument, StatusType, \
    CountrySpecificStatus, CountrySpecificDocument, CountrySpecificLevel, Organization, DynamicField, \
    CountrySpecificField, CommissionStructure, AssessmentRequest, InterviewStatusType, PartnerOnBoardingRequest, \
    UniversityInterviewStatus, Condition, UpdateNews, Webinar, UniversityCommissionType, StudentSlab, \
    CommissionFromUniversity, DailyProgressReport


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created')
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(CommissionStructure)
class CommissionStructureAdmin(admin.ModelAdmin):
    list_display = ["id", 'country', 'university', "year", "commission", "is_active", "created"]
    list_filter = ["is_active", "year"]
    search_fields = ['country__country_name', "university__name"]


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_filter = ['is_active']


@admin.register(PartnerSupportDocument)
class PartnerSupportDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'university', 'template', 'intake', 'year', 'is_active']
    list_filter = ['is_active']
    search_fields = ['template__name']


@admin.register(StatusType)
class StatusTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'priority', 'is_active', 'created', 'modified']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(CountrySpecificStatus)
class CountrySpecificStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'is_active', 'created', 'modified']
    list_filter = ['is_active']
    search_fields = ['country__country_name']


@admin.register(CountrySpecificDocument)
class CountrySpecificDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'is_active', 'created', 'modified']
    list_filter = ['is_active']
    search_fields = ['country__country_name']


@admin.register(CountrySpecificLevel)
class CountrySpecificLevelAdmin(admin.ModelAdmin):
    list_display = ['id', 'country', 'is_active', 'created', 'modified']
    list_filter = ['is_active']
    search_fields = ['country__country_name']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'course', 'current_status', 'intake', 'year', 'is_active', 'created', 'modified']
    list_filter = ['is_active']
    search_fields = ['student__name', 'course__name']


@admin.register(ApplicationStatusLog)
class ApplicationStatusLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'status', 'is_active', 'created', 'modified']
    list_filter = ['is_active', 'status']


@admin.register(ApplicationRemark)
class ApplicationRemarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'author', 'is_active', 'created', 'modified']
    list_filter = ['is_active']
    search_fields = ['message']


@admin.register(StaffingRequirement)
class StaffingRequirementAdmin(admin.ModelAdmin):
    list_display = ['target_value', 'rm_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['target_value']


@admin.register(UniversityTarget)
class UniversityTargetAdmin(admin.ModelAdmin):
    list_display = ['university', 'intake', 'year', 'target', 'is_active']
    list_filter = ['is_active']
    search_fields = ['university__name']


@admin.register(RMTarget)
class RMTargetAdmin(admin.ModelAdmin):
    list_display = ['rm', 'university', 'partner', 'intake', 'year', 'target', 'is_active']
    list_filter = ['is_active', 'intake', 'year']
    search_fields = ['rm__user__name', 'partner__company_name', 'university__name']


admin.site.register(GenericRemark)
admin.site.register(GenericFollowUp)
admin.site.register(GenericDocument)
admin.site.register(ApplicationAttribute)
admin.site.register(RMUniversityIntake)
admin.site.register(DynamicField)
admin.site.register(CountrySpecificField)
admin.site.register(AssessmentRequest)
admin.site.register(InterviewStatusType)
admin.site.register(UniversityInterviewStatus)
admin.site.register(InterviewActivity)
admin.site.register(Condition)


@admin.register(PartnerOnBoardingRequest)
class PartnerOnBoardingRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'company_name', 'is_active', ]


@admin.register(ApplicationAssignmentLog)
class ApplicationAssignmentLogAdmin(admin.ModelAdmin):
    list_display = ['application', 'assigned_to', 'assigned_by', 'created', 'modified']
    list_filter = ['created']
    search_fields = ['application', 'assigned_to', 'assigned_by']


@admin.register(UpdateNews)
class UpdateNewsAdmin(admin.ModelAdmin):
    list_display = ['country', 'created_by', 'created']


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ['id', 'university', 'webinar_for']


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['topic', 'object_id', 'created_by', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['topic']


@admin.register(Message)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['thread', 'sender', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['content']


@admin.register(UniversityCommissionType)
class UniversityCommissionTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'commission_type']
    list_filter = ['created']


@admin.register(StudentSlab)
class StudentSlabAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_student']


@admin.register(CommissionFromUniversity)
class CommissionFromUniversityAdmin(admin.ModelAdmin):
    list_display = ['university', 'commission_type', 'created_by']
    list_filter = ['created']


@admin.register(DailyProgressReport)
class DailyProgressReportAdmin(admin.ModelAdmin):
    list_display = ['activity_date', 'task_partner', 'created_by']
    search_fields = ['activity_date', 'task_partner']
