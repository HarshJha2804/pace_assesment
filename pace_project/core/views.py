import csv
from datetime import datetime
from decimal import Decimal
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django_boost.views.mixins import StaffMemberRequiredMixin

from pace_project.core.enums import StatusTypeEnum
from pace_project.core.forms import DocumentForm, StatusTypeForm, CountrySpecificStatusForm, StaffingRequirementForm, \
    UniversityTargetForm, RMTargetForm, CountrySpecificDocumentForm, CountrySpecificLevelForm, DynamicFieldTypeForm, \
    CountrySpecificFieldForm, ConditionForm
from pace_project.core.mixins import AMRequiredMixin, CMPORequiredMixin
from pace_project.core.models.target_models import UniversityTarget, RMTarget, RMUniversityIntake
from pace_project.core.models.requirement_models import StaffingRequirement
from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import DocumentTemplate, StatusType, CountrySpecificStatus, \
    CountrySpecificDocument, CountrySpecificLevel, DynamicField, CountrySpecificField, Condition
from pace_project.paceapp.models import University, Intake, Year, Country
from pace_project.users.models import Partner, Employee, User, ApplicationManager, UGStudentAcademic, PGStudentAcademic
from pace_project.paceapp.enums import ActivityStreamVerb, RoleEnum
from django.core.cache import cache


class DocumentTemplateCreateView(CreateView):
    model = DocumentTemplate
    form_class = DocumentForm
    template_name = "core/document_template_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Document Added Successfully!')
        return reverse("core:document_template_list")


class DocumentTemplateListView(ListView):
    model = DocumentTemplate
    template_name = "core/document_template_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class DocumentTemplateUpdateView(UpdateView):
    model = DocumentTemplate
    form_class = DocumentForm
    template_name = "core/document_template_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Document has been successfully updated!')
        return reverse("core:document_template_list")


class DocumentTemplateDeleteView(DeleteView):
    model = DocumentTemplate
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Document Deleted Successfully!')
        return reverse("core:document_template_list")


class StatusTypeCreateView(CreateView):
    model = StatusType
    form_class = StatusTypeForm
    template_name = "core/status_type/status_type_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Status Type Added Successfully!')
        return reverse("core:status_type_list")


class StatusTypeListView(ListView):
    model = StatusType
    template_name = "core/status_type/status_type_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class StatusTypeUpdateView(UpdateView):
    model = StatusType
    form_class = StatusTypeForm
    template_name = "core/status_type/status_type_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Status Type has been successfully updated!')
        return reverse("core:status_type_list")


class StatusTypeDeleteView(DeleteView):
    model = StatusType
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Status Type Deleted Successfully!')
        return reverse("core:status_type_list")


class DynamicFieldListView(ListView):
    model = DynamicField
    template_name = 'paceapp/dynamic_field/dynamic_field_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class DynamicFieldCreateView(CreateView):
    model = DynamicField
    form_class = DynamicFieldTypeForm
    template_name = 'paceapp/dynamic_field/dynamic_field_create.html'

    def get_success_url(self):
        messages.success(self.request, 'Dynamic Field Added Successfully!')
        return reverse("core:dynamic_field_list")


class DynamicFieldUpdateView(UpdateView):
    model = DynamicField
    form_class = DynamicFieldTypeForm
    template_name = 'paceapp/dynamic_field/dynamic_field_create.html'

    def get_success_url(self):
        messages.success(self.request, 'Dynamic Field has been successfully updated!')
        return reverse("core:dynamic_field_list")


class DynamicFieldDeleteView(DeleteView):
    model = DynamicField
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Dynamic Field Deleted Successfully!')
        return reverse("core:dynamic_field_list")


class CountrySpecificStatusCreateView(CreateView):
    model = CountrySpecificStatus
    form_class = CountrySpecificStatusForm
    template_name = "core/country_specific_status/country_specific_status_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Status Added Successfully!')
        return reverse("core:country_specific_status_list")


class CountrySpecificStatusDetailView(DetailView):
    model = CountrySpecificStatus
    template_name = "core/country_specific_status/country_specific_status_detail.html"


class CountrySpecificStatusListView(ListView):
    model = CountrySpecificStatus
    template_name = "core/country_specific_status/country_specific_status_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('country')
        country = self.request.GET.get('country')
        status_types = self.request.GET.getlist('status_types')
        status = self.request.GET.get('status')

        if country:
            queryset = queryset.filter(country__country_name__icontains=country)

        if status_types:
            queryset = queryset.filter(status_types__id__in=status_types).distinct()

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class CountrySpecificStatusUpdateView(UpdateView):
    model = CountrySpecificStatus
    form_class = CountrySpecificStatusForm
    template_name = "core/country_specific_status/country_specific_status_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Status has been successfully updated!')
        return reverse("core:country_specific_status_list")


class CountrySpecificDocumentCreateView(CreateView):
    model = CountrySpecificDocument
    form_class = CountrySpecificDocumentForm
    template_name = 'core/country_specific_document/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Document Added Successfully!')
        return reverse("core:country_specific_document_list")


class CountrySpecificDocumentListView(ListView):
    model = CountrySpecificDocument
    template_name = "core/country_specific_document/country_specific_document_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('country')
        country = self.request.GET.get('country')
        status = self.request.GET.get('status')

        if country:
            queryset = queryset.filter(country__country_name__icontains=country)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class CountrySpecificDocumentUpdateView(UpdateView):
    model = CountrySpecificDocument
    form_class = CountrySpecificDocumentForm
    template_name = "core/country_specific_document/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Document has been successfully updated!')
        return reverse("core:country_specific_document_list")


class CountrySpecificDocumentDetailView(DetailView):
    model = CountrySpecificDocument
    template_name = "core/country_specific_document/country_specific_document_detail.html"


class CountrySpecificDocumentDeleteView(DeleteView):
    model = CountrySpecificDocument
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Document Deleted Successfully!')
        return reverse("core:country_specific_document_list")


class StaffingRequirementCreateView(CreateView):
    model = StaffingRequirement
    form_class = StaffingRequirementForm
    template_name = "core/staffing_requirement/staffing_requirement_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Team Requirement Added Successfully!')
        return reverse("core:staffing_requirement_list")


class StaffingRequirementListView(ListView):
    model = StaffingRequirement
    template_name = "core/staffing_requirement/staffing_requirement_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        target_value = self.request.GET.get('target_value')
        rm_count = self.request.GET.get('rm_count')
        assessment_officer_count = self.request.GET.get('assessment_officer_count')
        application_manager_count = self.request.GET.get('application_manager_count')
        interviewer_count = self.request.GET.get('interviewer_count')
        visa_officer_count = self.request.GET.get('visa_officer_count')
        is_active = self.request.GET.get('is_active')

        if target_value:
            queryset = queryset.filter(target_value__icontains=target_value)

        if rm_count:
            queryset = queryset.filter(rm_count__icontains=rm_count)

        if assessment_officer_count:
            queryset = queryset.filter(assessment_officer_count__icontains=assessment_officer_count)

        if application_manager_count:
            queryset = queryset.filter(application_manager_count__icontains=application_manager_count)

        if interviewer_count:
            queryset = queryset.filter(interviewer_count__icontains=interviewer_count)

        if visa_officer_count:
            queryset = queryset.filter(visa_officer_count__icontains=visa_officer_count)

        if is_active in ['True', 'False']:
            queryset = queryset.filter(is_active=is_active)

        return queryset


class StaffingRequirementUpdateView(UpdateView):
    model = StaffingRequirement
    form_class = StaffingRequirementForm
    template_name = "core/staffing_requirement/staffing_requirement_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Team Requirement has been successfully updated!')
        return reverse("core:staffing_requirement_list")


class StaffingRequirementDeleteView(DeleteView):
    model = StaffingRequirement
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Team Requirement Deleted Successfully!')
        return reverse("core:staffing_requirement_list")


class UniversityTargetCreateView(CreateView):
    model = UniversityTarget
    form_class = UniversityTargetForm
    template_name = "core/university_target/university_target_form.html"

    def get_success_url(self):
        messages.success(self.request, 'University target Added Successfully!')
        return reverse("core:university_target_list")


class UniversityTargetListView(ListView):
    model = UniversityTarget
    template_name = "core/university_target/university_target_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        university = self.request.GET.get('university')
        intake = self.request.GET.get('intake')
        year = self.request.GET.get('year')
        target = self.request.GET.get('target')
        status = self.request.GET.get('status')

        if university:
            queryset = queryset.filter(university__name__icontains=university)

        if intake:
            queryset = queryset.filter(intake__intake_month__icontains=intake)

        if year:
            queryset = queryset.filter(year__intake_year__icontains=year)

        if target:
            queryset = queryset.filter(target__icontains=target)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class UniversityTargetUpdateView(UpdateView):
    model = UniversityTarget
    form_class = UniversityTargetForm
    template_name = "core/university_target/university_target_form.html"

    def get_success_url(self):
        messages.success(self.request, 'University Target has been successfully updated!')
        return reverse("core:university_target_list")


class UniversityTargetDeleteView(DeleteView):
    model = UniversityTarget
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'University Target Deleted Successfully!')
        return reverse("core:university_target_list")


class ApplicationListView(StaffMemberRequiredMixin, ListView):
    model = Application
    template_name = 'core/application/application_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'student',
            'student__partner',
            'student__study_country',
            'course',
            'course__university',
            'intake',
            'year',
            'student__study_level',
            'current_status',
            'created_by',
            'created_by__employee',
        ).prefetch_related(
            'remarks',
            'student__ugstudentacademic',
            'student__pgstudentacademic',
            'student__pgstudentacademic__english_test_type',
            'student__pgstudentacademic__sub_stream',
            'student__pgstudentacademic__board',
        ).order_by('-created')

        # Employee-specific filtering
        user = self.request.user
        if not user.is_superuser:
            employee = get_object_or_404(Employee, user=user)
            queryset = queryset.filter(course__university__in=employee.get_assigned_universities)

        # Apply filters
        filters = {
            'student__first_name__icontains': self.request.GET.get('student'),
            'student__passport_number__icontains': self.request.GET.get('passport_number'),
            'student__date_of_birth__icontains': self.request.GET.get('date_of_birth'),
            'course__country__id': self.request.GET.get('country'),
            'course__university__id': self.request.GET.get('university'),
            'student__partner_id': self.request.GET.get('agent_name'),
            'student__partner__city__icontains': self.request.GET.get('agent_city'),
            'course__level__icontains': self.request.GET.get('level'),
            'course__name__icontains': self.request.GET.get('course'),
            'current_status_id': self.request.GET.get('current_status'),
            'intake_id': self.request.GET.get('intake'),
            'year_id': self.request.GET.get('year'),
        }
        filters = {k: v for k, v in filters.items() if v}

        filter = self.request.GET.get('status')
        date = self.request.GET.get('date')

        university_id = self.request.GET.get('university_id')

        if filter:
            queryset = queryset.filter(current_status__name=filter)

        if date:
            try:
                date_obj = datetime.strptime(date, "%d-%m-%Y").date()
                queryset = queryset.filter(
                    Q(status_logs__status__name__iexact=filter) &
                    Q(status_logs__created__date=date_obj)
                ).distinct()
            except ValueError:
                print("Invalid date format")

        if university_id:
            queryset = queryset.filter(course__university_id=university_id)

        if filters:
            queryset = queryset.filter(**filters)

        return queryset

    def get(self, request, *args, **kwargs):
        if request.GET.get('export_csv') == 'true':
            filtered_queryset = self.get_queryset()
            return self.export_to_csv(filtered_queryset)

        return super().get(request, *args, **kwargs)

    def export_to_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'S.N.', 'Status', 'Student Name', 'Passport Number', 'Date Of Birth', 'Partner', 'Agent City', 'Country',
            'University', 'Course', 'Course Level', 'Intake', 'Year', 'Medical Status',
            'Funds Status', 'Interview Status', 'Created At', 'applied on', 'Created By', 'Remarks',
            'Stream', 'Sub stream', '12th English Marks', 'Passing Year', 'Overall Percentage',
            '12th Board', 'English Language', 'Academic Pathway', 'Conditions',

        ])
        for index, application in enumerate(queryset.distinct(), start=1):
            student = application.student
            twelfth_english_marks = passing_year = overall_percentage = twelfth_board = english_language = '-'
            academic_pathway = '-'

            academic_object = student.get_academic_object
            if academic_object:
                twelfth_english_marks = academic_object.twelfth_english_marks or '-'
                passing_year = academic_object.passing_year.intake_year if academic_object.passing_year else '-'
                overall_percentage = f"{academic_object.tenth_marks}%" if academic_object.tenth_marks else '-'
                twelfth_board = academic_object.board if academic_object.board else '-'
                english_language = academic_object.english_test_type if academic_object.english_test_type else '-'

                # Handle academic pathway based on model type
                if isinstance(academic_object, UGStudentAcademic):
                    academic_pathway = dict(UGStudentAcademic.ACADEMIC_PATHWAY_CHOICES).get(
                        academic_object.academic_pathway, '-') or '-'
                elif isinstance(academic_object, PGStudentAcademic):
                    academic_pathway = dict(PGStudentAcademic.ACADEMIC_PATHWAY_CHOICES).get(
                        academic_object.academic_pathway, '-') or '-'

            # Fetch conditions
            conditions_list = application.conditions.filter(is_active=True).values_list('name', flat=True)
            conditions = ', '.join(conditions_list) if conditions_list else '-'

            # Fetch the latest remark
            latest_remark = application.get_remarks.filter(is_active=True).latest('created').message \
                if application.get_remarks.filter(is_active=True).exists() else '-'

            writer.writerow([
                index,
                application.current_status.name if application.current_status else '-',
                f"{application.student.first_name} {application.student.middle_name or ''} {application.student.last_name or ''}".strip(),
                application.student.passport_number if application.student.passport_number else '-',
                application.student.date_of_birth if application.student.date_of_birth else '-',
                application.student.partner.company_name if application.student.partner else '-',
                application.student.partner.city if application.student.partner else '-',
                application.course.country.country_name if application.course.country else '-',
                application.course.university.name if application.course.university else '-',
                application.course.name if application.course.university else '-',
                application.course.level or '-',
                application.intake.intake_month if application.intake else '-',
                application.year.intake_year if application.year else '-',
                application.medical_status if application.medical_status else '-',
                application.funds_status if application.funds_status else '-',
                application.interview_status if application.interview_status else '-',
                application.created.strftime('%Y-%m-%d'),
                application.modified.strftime('%Y-%m-%d'),
                f"{application.created_by.name}" if application.created_by else '-',
                latest_remark,
                application.course.stream if application.course.stream else '-',
                application.course.substream if application.course.substream else '-',
                twelfth_english_marks,
                passing_year,
                overall_percentage,
                twelfth_board,
                english_language,
                academic_pathway,
                conditions

            ])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        # assigned_country = self.assigned_country
        # country_status = CountrySpecificStatus.objects.filter(country=assigned_country, is_active=True)
        rms_filtered = []
        seen_combinations = set()
        rms = RMTarget.objects.filter(
            university_id__in=queryset.values_list('course__university', flat=True).distinct(),
            intake_id__in=queryset.values_list('intake', flat=True).distinct(),
            year_id__in=queryset.values_list('year', flat=True).distinct(),
            is_active=True
        ).select_related('rm', 'rm__user')

        for rm in rms:
            key = (rm.university_id, rm.intake_id, rm.year_id, rm.rm.user.name)
            if key not in seen_combinations:
                seen_combinations.add(key)
                rms_filtered.append(rm)

        context['rms'] = rms_filtered
        context['university'] = University.objects.all()
        context['countries'] = Country.objects.filter()
        context['partners'] = Partner.objects.all()
        context['intakes'] = Intake.objects.all()
        context['years'] = Year.objects.all()
        context['statuses'] = StatusType.objects.filter()
        return context


class ApplicationPendingFromIOAListView(AMRequiredMixin, ListView):
    model = Application
    template_name = "dashboard/application_manager/application_pending_from_ioa_list.html"
    paginate_by = 20
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user
        employee = get_object_or_404(Employee, user=user)

        return Application.objects.filter(
            is_active=True,
            current_status__name=ActivityStreamVerb.APPLICATION_PENDING_FROM_IOA.value,
            course__university__in=employee.get_assigned_universities
        ).order_by('-created')


class ApplicationPendingFromAgentListView(AMRequiredMixin, ListView):
    model = Application
    template_name = "dashboard/application_manager/application_pending_from_agent_list.html"
    paginate_by = 20
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user
        employee = get_object_or_404(Employee, user=user)

        return Application.objects.filter(
            is_active=True,
            current_status__name=ActivityStreamVerb.APPLICATION_PENDING_FROM_AGENT.value,
            course__university__in=employee.get_assigned_universities
        ).order_by('-created')


class ApplicationSubmittedView(AMRequiredMixin, ListView):
    model = Application
    template_name = "dashboard/application_manager/application_submitted.html"
    paginate_by = 20
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user
        employee = get_object_or_404(Employee, user=user)

        return Application.objects.filter(
            is_active=True,
            current_status__name=ActivityStreamVerb.APPLICATION_SUBMITTED.value,
            course__university__in=employee.get_assigned_universities
        ).order_by('-created')


class ComplianceApplicationListView(CMPORequiredMixin, ListView):
    model = Application
    template_name = "dashboard/compliance_officer/compliance_application_list.html"
    paginate_by = 20
    context_object_name = "applications"

    def get_queryset(self):
        queryset = Application.objects.filter(
            is_active=True,
            course__country=self.employee.assigned_country,
            course__university__in=self.employee.assigned_universities.all()
        ).prefetch_related('current_status')

        status_filter = self.request.GET.get('filter', None)
        if status_filter:
            queryset = queryset.filter(current_status__name=status_filter)

        student = self.request.GET.get('student')
        passport_number = self.request.GET.get('passport_number')
        country = self.request.GET.get('country')
        university = self.request.GET.get('university')
        agent_name = self.request.GET.get('agent_name')
        agent_city = self.request.GET.get('agent_city')
        level = self.request.GET.get('level')
        intake = self.request.GET.get('intake')
        year = self.request.GET.get('year')
        course = self.request.GET.get('course')
        current_status = self.request.GET.get('current_status')

        if student:
            queryset = queryset.filter(student__first_name__icontains=student)

        if passport_number:
            queryset = queryset.filter(student__passport_number__icontains=passport_number)

        if university:
            queryset = queryset.filter(course__university_id=university)

        if country:
            queryset = queryset.filter(course__country__id=country)

        if agent_name:
            queryset = queryset.filter(student__partner_id=agent_name)

        if agent_city:
            queryset = queryset.filter(student__partner__city__icontains=agent_city)

        if level:
            queryset = queryset.filter(level__icontains=level)

        if course:
            queryset = queryset.filter(course__name__icontains=course)

        if current_status:
            queryset = queryset.filter(current_status_id=current_status)

        if intake:
            queryset = queryset.filter(intake_id=intake)

        if year:
            queryset = queryset.filter(year_id=year)

        return queryset.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        rms_filtered = []
        seen_combinations = set()
        rms = RMTarget.objects.filter(
            university_id__in=queryset.values_list('course__university', flat=True).distinct(),
            intake_id__in=queryset.values_list('intake', flat=True).distinct(),
            year_id__in=queryset.values_list('year', flat=True).distinct(),
            is_active=True
        ).select_related('rm', 'rm__user')

        for rm in rms:
            key = (rm.university_id, rm.intake_id, rm.year_id, rm.rm.user.name)
            if key not in seen_combinations:
                seen_combinations.add(key)
                rms_filtered.append(rm)

        context['rms'] = rms_filtered
        assigned_country = self.employee.assigned_country
        country_status = CountrySpecificStatus.objects.filter(country=assigned_country, is_active=True)
        context['university'] = University.objects.all()
        context['countries'] = Country.objects.filter(country_name=assigned_country)
        context['partners'] = Partner.objects.all()
        context['intakes'] = Intake.objects.all()
        context['years'] = Year.objects.all()
        context['statuses'] = StatusType.objects.filter(country_specific_statuses__in=country_status,
                                                        is_active=True).distinct()
        return context


class CountrySpecificStatusDeleteView(DeleteView):
    model = CountrySpecificStatus
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Status Deleted Successfully!')
        return reverse("core:country_specific_status_list")


class RMTargetCreateView(CreateView):
    model = RMTarget
    form_class = RMTargetForm
    template_name = 'core/rm_target/rm_target_form.html'

    def get_success_url(self):
        messages.success(self.request, 'RM Target Added Successfully!')
        return reverse("core:rm_target_list")


class RMTargetListView(ListView):
    model = RMTarget
    template_name = 'core/rm_target/rm_target_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('rm', 'university', 'partner', 'intake', 'year')
        rm = self.request.GET.get('rm_id')
        university = self.request.GET.get('university_id')
        partner = self.request.GET.get('partner_id')
        intake = self.request.GET.get('intake_id')
        year = self.request.GET.get('year_id')
        status = self.request.GET.get('status')

        if rm:
            queryset = queryset.filter(rm_id=rm)

        if university:
            queryset = queryset.filter(university_id=university)

        if partner:
            queryset = queryset.filter(partner_id=partner)

        if intake:
            queryset = queryset.filter(intake_id=intake)

        if year:
            queryset = queryset.filter(year_id=year)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        universities = cache.get('universities')
        partners = cache.get("partners")
        intakes = cache.get("intakes")
        years = cache.get("years")

        if not universities:
            universities = University.objects.all()
            cache.set('universities', universities, 3600)  # Cache for 1 hour

        if not partners:
            partners = Partner.objects.all()
            cache.set('partners', partners, 3600)  # Cache for 1 hour

        if not intakes:
            intakes = Intake.objects.all()
            cache.set('intakes', intakes, 86400)  # Cache for 1 day

        if not years:
            years = Year.objects.all()
            cache.set('years', years, 86400)  # Cache for 1 day

        context['universities'] = universities
        context['partners'] = partners
        context['intakes'] = intakes
        context['years'] = years
        return context


class RMTargetUpdateView(UpdateView):
    model = RMTarget
    form_class = RMTargetForm
    template_name = "core/rm_target/rm_target_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Regional Marketing Head Target has been successfully updated!')
        return reverse("core:rm_target_list")


class RMTargetDeleteView(DeleteView):
    model = RMTarget
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'University Target Deleted Successfully!')
        return reverse("core:rm_target_list")


class CountrySpecificLevelCreateView(CreateView):
    model = CountrySpecificLevel
    form_class = CountrySpecificLevelForm
    template_name = 'core/country_specific_level/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Level Added Successfully!')
        return reverse("core:country_specific_level_list")


class CountrySpecificLevelListView(ListView):
    model = CountrySpecificLevel
    template_name = "core/country_specific_level/country_specific_level_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('country')
        country = self.request.GET.get('country')
        status = self.request.GET.get('status')

        if country:
            queryset = queryset.filter(country__country_name__icontains=country)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class CountrySpecificLevelUpdateView(UpdateView):
    model = CountrySpecificLevel
    form_class = CountrySpecificLevelForm
    template_name = "core/country_specific_level/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Level Updated Successfully!')
        return reverse("core:country_specific_level_list")


class CountrySpecificLevelDeleteView(DeleteView):
    model = CountrySpecificLevel
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Level Deleted Successfully!')
        return reverse("core:country_specific_level_list")


class CountrySpecificLevelDetailView(DetailView):
    model = CountrySpecificLevel
    template_name = "core/country_specific_level/country_specific_detail_level.html"


class ApplicationDetailView(StaffMemberRequiredMixin, DetailView):
    model = Application
    template_name = "core/application/_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.student.get_documents
        return context


class RegionalMarketingTargetsListView(StaffMemberRequiredMixin, ListView):
    model = RMTarget
    template_name = 'dashboard/regional_marketing_head/target.html'
    paginate_by = 20

    def get_queryset(self):
        employee = self.request.user.employee
        active_intakes = RMUniversityIntake.objects.filter(rm=employee, is_active=True).values('intake_id')
        queryset = super().get_queryset().filter(
            rm=employee,
            intake_id__in=active_intakes,
            is_active=True
        )
        name = self.request.GET.get('name')
        country = self.request.GET.get('country')
        if name:
            queryset = queryset.filter(partner__company_name__icontains=name)
        if country:
            queryset = queryset.filter(partner__country__id=country)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context


class PremiumPartnerListView(ListView):
    model = RMTarget
    template_name = 'dashboard/regional_marketing_head/premier_partner.html'
    paginate_by = 20

    def get_queryset(self):
        employee = self.request.user.employee
        active_intakes = RMUniversityIntake.objects.filter(rm=employee, is_active=True).values('intake_id')
        queryset = super().get_queryset().filter(
            rm=employee,
            intake_id__in=active_intakes,
            is_active=True
        )
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        country = self.request.GET.get('country')
        status = self.request.GET.get('status')
        mobile_number = self.request.GET.get('mobile_number')

        filter_type = self.request.GET.get('filter')

        if filter_type == "pending-commission":
            queryset = queryset.filter(
                Q(partner__partner_commissions__isnull=True) | Q(
                    partner__partner_commissions__commission=Decimal('0.00'))
            ).distinct()

        if name:
            queryset = queryset.filter(partner__company_name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(partner__is_active=status)

        if email:
            queryset = queryset.filter(partner__email__icontains=email)

        if country:
            queryset = queryset.filter(partner__country__id=country)

        if mobile_number:
            queryset = queryset.filter(partner__mobile_number__icontains=mobile_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        user = self.request.user
        for rm_target in context['object_list']:
            rm_target.can_update_commission = rm_target.partner.partner_commissions.filter(created_by=user).exists()
        return context


class CountrySpecificFieldCreateView(CreateView):
    model = CountrySpecificField
    form_class = CountrySpecificFieldForm
    template_name = 'core/country_specific_field/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Field Added Successfully!')
        return reverse("core:country_specific_field_list")


class CountrySpecificFieldListView(ListView):
    model = CountrySpecificField
    template_name = "core/country_specific_field/country_specific_field_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('country')
        country = self.request.GET.get('country')
        status = self.request.GET.get('status')

        if country:
            queryset = queryset.filter(country__country_name__icontains=country)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class CountrySpecificFieldUpdateView(UpdateView):
    model = CountrySpecificField
    form_class = CountrySpecificFieldForm
    template_name = "core/country_specific_field/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Field Updated Successfully!')
        return reverse("core:country_specific_field_list")


class CountrySpecificFieldDeleteView(DeleteView):
    model = CountrySpecificField
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Country Specific Field Deleted Successfully!')
        return reverse("core:country_specific_field_list")


class CountrySpecificFieldDetailView(DetailView):
    model = CountrySpecificField
    template_name = "core/country_specific_field/country_specific_field_detail.html"


class RMApplicationListView(ListView):
    model = Application
    template_name = 'dashboard/regional_marketing_head/all_application_list.html'
    paginate_by = 20

    def get_queryset(self):
        employee = self.request.user.employee
        assigned_universities = employee.assigned_universities.filter(is_active=True)
        active_intakes = RMUniversityIntake.objects.filter(rm=employee, is_active=True).values('intake_id')
        active_year = RMUniversityIntake.objects.filter(rm=employee, is_active=True).values('year_id')

        partners = RMTarget.objects.filter(rm=employee, intake_id__in=active_intakes).values('partner')

        # Filter applications based on the logged-in employee's universities and partners
        queryset = Application.objects.filter(
            is_active=True,
            student__partner__id__in=partners,
            course__university__in=assigned_universities,
            year__id__in=active_year,
            intake__id__in=active_intakes
        )
        filter_type = self.request.GET.get('status')
        if filter_type:
            queryset = queryset.filter(current_status__name=filter_type)

        name = self.request.GET.get('student')
        course = self.request.GET.get('course')
        intake = self.request.GET.get('intake')

        if name:
            queryset = queryset.filter(Q(student__first_name__icontains=name) | Q(student__last_name__icontains=name))

        if course:
            queryset = queryset.filter(course__name__icontains=course)

        if intake:
            queryset = queryset.filter(intake__intake_month__icontains=intake)

        return queryset


class ApplicationManagerApplicationListView(AMRequiredMixin, ListView):
    model = Application
    template_name = "dashboard/application_manager/Application_manager_list.html"
    paginate_by = 20
    context_object_name = "applications"

    def get_queryset(self):
        application_manager = ApplicationManager.objects.filter(employee=self.employee).first()
        statuses = {
            'submitted': ActivityStreamVerb.APPLICATION_SUBMITTED.value,
            'pending_from_ioa': ActivityStreamVerb.APPLICATION_PENDING_FROM_IOA.value,
            'pending_from_agent': ActivityStreamVerb.APPLICATION_PENDING_FROM_AGENT.value,
            'prescreening_pending': ActivityStreamVerb.PRESCREENING_PENDING.value
        }

        valid_statuses = statuses.values()
        queryset = Application.objects.filter(is_active=True, current_status__name__in=valid_statuses)

        if application_manager.is_head:
            queryset = queryset.filter(course__university__in=self.employee.get_assigned_universities)
        else:
            queryset = queryset.filter(application_manager=self.employee.user)

        # Handle unassigned application manager filter
        unassigned_manager = self.request.GET.get('unassigned_manager')
        if unassigned_manager == 'true':
            queryset = queryset.filter(application_manager__isnull=True)

        filter_type = self.request.GET.get('filter')
        if filter_type in statuses:
            queryset = queryset.filter(current_status__name=statuses[filter_type])

        student = self.request.GET.get('student')
        passport_number = self.request.GET.get('passport_number')
        country = self.request.GET.get('country')
        university = self.request.GET.get('university')
        agent_name = self.request.GET.get('agent_name')
        agent_city = self.request.GET.get('agent_city')
        level = self.request.GET.get('level')
        intake = self.request.GET.get('intake')
        year = self.request.GET.get('year')
        course = self.request.GET.get('course')
        current_status = self.request.GET.get('current_status')

        if student:
            queryset = queryset.filter(student__first_name__icontains=student)

        if passport_number:
            queryset = queryset.filter(student__passport_number__icontains=passport_number)

        if university:
            queryset = queryset.filter(university__icontains=university)

        if country:
            queryset = queryset.filter(course__country__id=country)

        if agent_name:
            queryset = queryset.filter(student__partner_id=agent_name)

        if agent_city:
            queryset = queryset.filter(student__partner__city__icontains=agent_city)

        if level:
            queryset = queryset.filter(level__icontains=level)

        if course:
            queryset = queryset.filter(course__name__icontains=course)

        if current_status:
            queryset = queryset.filter(current_status__name__icontains=current_status)

        if intake:
            queryset = queryset.filter(intake_id=intake)

        if year:
            queryset = queryset.filter(year_id=year)

        return queryset.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        assigned_country = self.employee.assigned_country
        country_status = CountrySpecificStatus.objects.filter(country=assigned_country, is_active=True)
        rms_filtered = []
        seen_combinations = set()
        rms = RMTarget.objects.filter(
            university_id__in=queryset.values_list('course__university', flat=True).distinct(),
            intake_id__in=queryset.values_list('intake', flat=True).distinct(),
            year_id__in=queryset.values_list('year', flat=True).distinct(),
            is_active=True
        ).select_related('rm', 'rm__user')

        for rm in rms:
            key = (rm.university_id, rm.intake_id, rm.year_id, rm.rm.user.name)
            if key not in seen_combinations:
                seen_combinations.add(key)
                rms_filtered.append(rm)

        context['rms'] = rms_filtered
        context['university'] = University.objects.all()
        context['countries'] = Country.objects.filter(country_name=assigned_country)
        context['partners'] = Partner.objects.all()
        context['intakes'] = Intake.objects.all()
        context['years'] = Year.objects.all()
        context['statuses'] = StatusType.objects.filter(country_specific_statuses__in=country_status,
                                                        is_active=True).distinct()
        return context


class AssignApplicationManagerApplicationListView(AMRequiredMixin, ListView):
    model = Application
    template_name = "dashboard/application_manager/assign_application_manager_list.html"
    paginate_by = 20
    context_object_name = "applications"

    def get_queryset(self):
        user = self.request.user
        employee = get_object_or_404(Employee, user=user)

        statuses = {
            'submitted': ActivityStreamVerb.APPLICATION_SUBMITTED.value,
            'pending_from_ioa': ActivityStreamVerb.APPLICATION_PENDING_FROM_IOA.value,
            'pending_from_agent': ActivityStreamVerb.APPLICATION_PENDING_FROM_AGENT.value,
            'prescreening_pending': ActivityStreamVerb.PRESCREENING_PENDING.value
        }

        valid_statuses = statuses.values()

        queryset = Application.objects.filter(
            is_active=True,
            course__university__in=employee.get_assigned_universities,
            current_status__name__in=valid_statuses
        )

        # Handle unassigned application manager filter
        unassigned_manager = self.request.GET.get('unassigned_manager')
        if unassigned_manager == 'true':
            queryset = queryset.filter(application_manager__isnull=True)

        filter_type = self.request.GET.get('filter')
        if filter_type in statuses:
            queryset = queryset.filter(current_status__name=statuses[filter_type])

        student = self.request.GET.get('student')
        course = self.request.GET.get('course')
        current_status = self.request.GET.get('current_status')
        intake = self.request.GET.get('intake')
        year = self.request.GET.get('year')

        if student:
            queryset = queryset.filter(student__first_name__icontains=student)

        if course:
            queryset = queryset.filter(course__name__icontains=course)

        if current_status:
            queryset = queryset.filter(current_status__name__icontains=current_status)

        if intake:
            queryset = queryset.filter(intake__intake_month__icontains=intake)

        if year:
            queryset = queryset.filter(year__intake_year__icontains=year)

        return queryset.order_by('-created')


class AMApplicationDetailView(AMRequiredMixin, DetailView):
    model = Application
    template_name = "dashboard/application_manager/am_application_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()

        if application.course.university:
            available_managers = Employee.objects.filter(
                user__role__name=RoleEnum.APPLICATION_MANAGER.value,
                assigned_universities=application.course.university
            )
        else:

            available_managers = Employee.objects.none()

        context['available_managers'] = available_managers

        user = self.request.user
        if hasattr(user, 'employee'):
            assigned_universities = user.employee.assigned_universities.filter(is_active=True)
        else:
            assigned_universities = University.objects.filter(is_active=True)

        context['applications'] = Application.objects.filter(
            student=application.student,
            course__university__in=assigned_universities
        )

        # Adding student and student_id to context
        student = application.student
        context['student'] = student
        context['student_id'] = student.pk
        context['documents'] = student.get_documents

        return context

    def post(self, request, *args, **kwargs):
        application_id = request.POST.get('application_id')
        manager_id = request.POST.get('am')

        application = get_object_or_404(Application, id=application_id)
        manager = get_object_or_404(User, id=manager_id)

        application.application_manager = manager
        application.save()

        return redirect(
            reverse('paceapp:application_manager_application_list') + '?' + request.META.get('QUERY_STRING'))


class UniversityApplicationsListView(ListView):
    model = Application
    template_name = 'dashboard/university_dashboard.html'
    context_object_name = 'applications'

    def get_queryset(self):
        # Get the university ID from the URL parameters
        university_id = self.kwargs.get('university_id')
        queryset = super().get_queryset().select_related(
            'student',
            'student__partner',
            'student__study_country',
            'course',
            'course__university',
            'intake',
            'year',
            'student__study_level',
            'current_status',
            'created_by',
            'created_by__employee',
        ).prefetch_related(
            'remarks',
            'student__ugstudentacademic',
            'student__pgstudentacademic',
            'student__pgstudentacademic__english_test_type',
            'student__pgstudentacademic__sub_stream',
            'student__pgstudentacademic__board'
        ).order_by('-created')

        user = self.request.user
        if not user.is_superuser:
            employee = get_object_or_404(Employee, user=user)
            queryset = queryset.filter(course__university__in=employee.get_assigned_universities)

        # Filter by university if specified
        if university_id:
            queryset = queryset.filter(course__university_id=university_id)

        # Apply additional filters based on query parameters
        student = self.request.GET.get('student')
        course = self.request.GET.get('course')
        intake = self.request.GET.get('intake')
        year = self.request.GET.get('year')
        status = self.request.GET.get('status')

        if student:
            queryset = queryset.filter(student__first_name__icontains=student)

        if course:
            queryset = queryset.filter(course__name__icontains=course)

        if intake:
            queryset = queryset.filter(intake__intake_month__icontains=intake)

        if year:
            queryset = queryset.filter(year__intake_year__icontains=year)

        if status:
            queryset = queryset.filter(current_status__id=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        university_id = self.kwargs.get('university_id')
        context['university'] = get_object_or_404(University, pk=university_id)
        return context


class RegionalMarketingHeadApplicationListView(ListView):
    model = Application
    template_name = 'dashboard/regional_marketing_head/_application_list.html'
    paginate_by = 20

    def get_queryset(self):
        employee = self.request.user.employee
        assigned_universities = employee.assigned_universities.filter(is_active=True)
        active_intakes = RMUniversityIntake.objects.filter(rm=employee, is_active=True).values('intake_id')
        active_year = RMUniversityIntake.objects.filter(rm=employee, is_active=True).values('year_id')

        partners = RMTarget.objects.filter(rm=employee, intake_id__in=active_intakes, year_id__in=active_year).values(
            'partner')
        status_list = [
            StatusTypeEnum.CONDITIONAL_OFFER_LETTER.value,
            StatusTypeEnum.UNCONDITIONAL_OFFER_LETTER.value,
            StatusTypeEnum.REVISED_OFFER_PENDING.value,
        ]
        # Filter applications based on the logged-in employee's universities and partners
        queryset = Application.objects.filter(
            is_active=True,
            student__partner__id__in=partners,
            course__university__in=assigned_universities,
            current_status__name__in=status_list,
            intake__id__in=active_intakes,
            year__id__in=active_year,
        )

        name = self.request.GET.get('student')
        course = self.request.GET.get('course')
        intake = self.request.GET.get('intake')

        if name:
            queryset = queryset.filter(Q(student__first_name__icontains=name) | Q(student__last_name__icontains=name))

        if course:
            queryset = queryset.filter(course__name__icontains=course)

        if intake:
            queryset = queryset.filter(intake__intake_month__icontains=intake)

        return queryset


class ConditionCreateView(CreateView):
    model = Condition
    form_class = ConditionForm
    template_name = "core/condition/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Condition Added Successfully!')
        return reverse("core:condition_list")


class ConditionListView(ListView):
    model = Condition
    template_name = "core/condition/_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in [True, False]:
            queryset = queryset.filter(status=status)

        return queryset


class UpdateConditionView(UpdateView):
    model = Condition
    form_class = ConditionForm
    template_name = "core/condition/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Condition Updated Successfully!')
        return reverse("core:condition_list")
