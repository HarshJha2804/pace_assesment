from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, Partner, PartnerBranch, Student, UGStudentAcademic, PGStudentAcademic, Employee, Role, \
    ApplicationManager, PartnerAgreement, ContactUs

from pace_project.users.models import PartnerCommunication

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.site.login = login_required(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                    "avatar",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "name", "role", "is_superuser", "date_joined"]
    search_fields = ["name"]
    ordering = ["-date_joined"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'mobile_number', 'country', 'is_active', 'created', 'modified']
    list_filter = ['created', 'onboarding_completed', 'blacklisted','is_active', 'country', 'state']
    search_fields = ['company_name', 'email', 'mobile_number']


@admin.register(PartnerBranch)
class PartnerBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner', 'country', 'state', 'created', 'modified', 'is_active']
    list_filter = ['is_active', 'country', 'state']
    search_fields = ['name', 'partner__name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'partner', 'date_of_birth', 'passport_number', 'modified', 'is_active']
    list_filter = ['is_active']
    search_fields = ['first_name', 'middle_name', 'last_name', 'partner__name']


@admin.register(UGStudentAcademic)
class UGStudentAcademicAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_pathway', 'country', 'board', 'state', 'stream', 'sub_stream', 'modified',
                    'is_active']
    list_filter = ['is_active', 'academic_pathway']
    search_fields = ['student_first_name', 'student_middle_name', 'student_last_name', 'student_partner__name']


@admin.register(PGStudentAcademic)
class PGStudentAcademicAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_pathway', 'country', 'board', 'state', 'stream', 'sub_stream', 'modified',
                    'is_active']
    list_filter = ['is_active', 'academic_pathway']
    search_fields = ['student_first_name', 'student_middle_name', 'student_last_name', 'student_partner__name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile_number', 'whatsapp_number', 'assigned_country', 'is_on_leave']
    list_filter = ['assigned_country', 'user__is_active']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['subject', 'description']
    list_filter = ['is_active']
    search_fields = ['subject', 'description']


@admin.register(PartnerCommunication)
class PartnerCommunicationAdmin(admin.ModelAdmin):
    list_display = ['partner', 'communication_type', 'communication_value', 'is_active']
    list_filter = ['communication_type', 'is_active']
    search_fields = ['partner__name', 'communication_value']


@admin.register(PartnerAgreement)
class PartnerAgreementAdmin(admin.ModelAdmin):
    list_display = ['partner', 'agreement',"year", 'is_active', 'created']
    list_filter = ['is_active']
    search_fields = ['partner__name', "year"]


@admin.register(ApplicationManager)
class ApplicationManagerAdmin(admin.ModelAdmin):
    list_display = ['employee', 'is_head', 'will_process_application', 'created']
