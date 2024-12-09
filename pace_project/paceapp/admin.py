from django.contrib import admin

from pace_project.paceapp.models import Country, Board, Level, Stream, Intake, Year, Campus, State, University, Course, \
    SubStream, UniBoardGap, EnglishTestType, EntryCriteria, EnglishTest, UniversityStateMapping, PGEntryCriteria, \
    AssessmentDiscovery, Region, UniversityIntake, UniversityAgreement

admin.site.register(Board)
admin.site.site_header = "Pace CRM Admin"
admin.site.site_title = "Pace CRM"
admin.site.index_title = "Welcome to Pace CRM"

admin.site.register(Level)
admin.site.register(SubStream)
admin.site.register(Stream)
admin.site.register(Intake)
admin.site.register(Year)
admin.site.register(Campus)
admin.site.register(EnglishTestType)
admin.site.register(EntryCriteria)
admin.site.register(EnglishTest)
admin.site.register(UniversityIntake)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'is_active', 'created', 'modified']
    list_filter = ['created', 'modified', 'is_active']
    search_fields = ['name', 'university__name']


@admin.register(UniversityStateMapping)
class UniversityStateMappingAdmin(admin.ModelAdmin):
    list_display = ['university', 'is_active', 'created', 'modified']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active']


@admin.register(UniBoardGap)
class UniBoardGapAdmin(admin.ModelAdmin):
    list_display = ['university', 'board', 'state', 'gap']


@admin.register(PGEntryCriteria)
class PGEntryCriteriaAdmin(admin.ModelAdmin):
    list_display = [
        'course', 'country', 'board',
        'twelfth_english_marks',
        'diploma_overall_marks',
        'ug_overall_marks',
        'level_diploma_marks',
        'is_active'
    ]
    list_filter = ['is_active']


@admin.register(AssessmentDiscovery)
class AssessmentDiscoveryAdmin(admin.ModelAdmin):
    list_display = ['student', 'is_processed', 'is_active']
    list_filter = ['is_processed', 'is_active']


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', "alis", 'email', 'country', 'is_active']


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_active']


@admin.register(UniversityAgreement)
class UniversityAgreementAdmin(admin.ModelAdmin):
    list_display = ['university', 'is_active']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['country_name', 'is_active', 'is_active_for_student', 'is_active_for_university']
