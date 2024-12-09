import logging
from allauth.account.views import SignupView
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib import messages
from django.core.cache import cache
from datetime import timedelta, datetime

from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin
from django_boost.views.mixins import StaffMemberRequiredMixin
from notifications.signals import notify
from django.db import transaction

from pace_project.core.enums import StatusTypeEnum
from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import StatusType, AssessmentRequest, Webinar, CountrySpecificStatus
from pace_project.paceapp.actstream import generate_new_application_stream
from pace_project.paceapp.enums import LevelEnum, RoleEnum
from pace_project.paceapp.models import University, Level, Year, Intake, AssessmentDiscovery, Country
from pace_project.paceapp.validators import has_application_manager_permission_dashboard, has_assessment_permission
from pace_project.partner.apis import api_news_desk_posts
from pace_project.partner.forms import PartnerSignupForm, PartnerAgreementForm, \
    ApplyApplicationForm, PartnerCommissionForm, SetPartnerCommissionForm
from pace_project.partner.mixins import PartnerRequiredMixin
from pace_project.partner.models import PartnerCommission, PartnerCommissionSetup
from pace_project.partner.services import sent_mail_to_university_on_ass_request
from pace_project.users.models import Student, Partner, UGStudentAcademic, PGStudentAcademic, PartnerAgreement, \
    ApplicationManager
from django.db.models import Q
from django.urls import reverse

from pace_project.utils.utils import get_assessment_officer

logger = logging.getLogger(__name__)


def redirect_view(request):
    return redirect(reverse("partner:dashboard_partner"))


class PartnerRegisterView(SignupView):
    template_name = "partner/register_form.html"
    form_class = PartnerSignupForm

    def get_form_class(self):
        return PartnerSignupForm


class PartnerDashboardView(PartnerRequiredMixin, TemplateView):
    template_name = 'dashboard/partner_dashboard/partner_dashboard.html'

    def get_application_count(self, status_type, user_data):
        return Application.objects.filter(
            current_status__name=status_type,
            student__partner__user=user_data
        ).count()

    def get_news_desk_posts(self, per_page):
        cache_key = f"news_desk_posts_{per_page}"
        cached_posts = cache.get(cache_key)
        if cached_posts:
            return cached_posts
        posts = api_news_desk_posts(per_page=per_page)
        if posts:
            cache.set(cache_key, posts, timeout=3600)  # Cache the result for 1 hour
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user_data = self.request.user
        ar_status = StatusTypeEnum.ASSESSMENT_REJECTED.value
        today_1 = datetime.now().date()
        yesterday_1 = today_1 - timedelta(days=1)
        yesterday_2 = today_1 - timedelta(days=2)

        partner_students = Student.objects.filter(partner=self.partner)
        total_rejected_assessment = partner_students.filter(is_active=True, assessment_status__name=ar_status).count()
        status_list = [
            StatusTypeEnum.APPLICATION_SUBMITTED.value,
            StatusTypeEnum.PRESCREENING_APPROVED.value
        ]

        total_student = Student.objects.filter(partner__user=user_data).count()
        total_application = Application.objects.filter(student__partner__user=user_data).count()

        total_offer_awaited = Application.objects.filter(current_status__name__in=status_list,
                                                         student__partner__user=user_data).count()

        total_application_pending_from_ioa = self.get_application_count(
            StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value, user_data)
        total_fee_paid = self.get_application_count(StatusTypeEnum.FEE_PAID.value, user_data)
        total_visa_grant = self.get_application_count(StatusTypeEnum.VISA_GRANT.value, user_data)
        total_visa_lodged = self.get_application_count(StatusTypeEnum.VISA_LODGED.value, user_data)
        total_visa_refused = self.get_application_count(StatusTypeEnum.VISA_REFUSED.value, user_data)
        total_application_pending_from_agent = self.get_application_count(
            StatusTypeEnum.APPLICATION_PENDING_FROM_AGENT.value, user_data)
        conditional_offer = self.get_application_count(StatusTypeEnum.CONDITIONAL_OFFER_LETTER.value, user_data)
        unconditional_offer = self.get_application_count(StatusTypeEnum.UNCONDITIONAL_OFFER_LETTER.value, user_data)
        revised_offer = self.get_application_count(StatusTypeEnum.REVISED_OFFER_PENDING.value, user_data)

        ass_received_students = AssessmentDiscovery.objects.filter(student__in=partner_students).values('student')

        total_received_assessment = AssessmentRequest.objects.filter(
            student__in=ass_received_students, is_active=True
        ).distinct('student').count()

        total_pending_assessment = AssessmentRequest.objects.filter(
            student__in=partner_students, is_active=True
        ).exclude(student__in=ass_received_students).distinct('student').count()

        context['total_student_count'] = total_student
        context['total_application'] = total_application
        context['total_offer_awaited'] = total_offer_awaited
        context['total_pending_assessment'] = total_pending_assessment
        context['total_received_assessment'] = total_received_assessment
        context['total_rejected_assessment'] = total_rejected_assessment
        context['total_application_pending_from_ioa'] = total_application_pending_from_ioa
        context['total_application_pending_from_agent'] = total_application_pending_from_agent
        context['total_fee_paid'] = total_fee_paid
        context['total_visa_grant'] = total_visa_grant
        context['total_visa_lodged'] = total_visa_lodged
        context['total_visa_refused'] = total_visa_refused
        context['conditional_offer'] = conditional_offer
        context['unconditional_offer'] = unconditional_offer
        context['revised_offer'] = revised_offer
        context['today'] = today_1
        context['yesterday'] = yesterday_1
        context['yesterday2'] = yesterday_2
        context['countries'] = Country.objects.filter(
            is_active=True, is_active_for_university=True
        ).order_by("priority")
        context['universities'] = University.objects.filter(
            is_active=True
        ).order_by("country__priority", "priority")[:5]
        context['webinars'] = Webinar.objects.filter(is_active=True).order_by("-created")
        context['years'] = Year.objects.current_to_future()
        context['levels'] = Level.objects.all()
        return context


class PartnerCountryDashboard(PartnerRequiredMixin, TemplateView):
    template_name = 'dashboard/partner_dashboard/partner_country_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        country_id = self.kwargs['pk']
        ctx['country_ids'] = get_object_or_404(Country, id=country_id)
        return ctx

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        country_id = self.kwargs['pk']
        self.country_specific_status = CountrySpecificStatus.objects.filter(
            country=country_id).prefetch_related('status_types')
        self.all_statuses = StatusType.objects.filter(
            country_specific_statuses__in=self.country_specific_status,
            is_active=True
        ).distinct().order_by('priority')

    def get_application_count(self, status_type, user_data):
        return Application.objects.filter(
            current_status__name=status_type,
            student__partner__user=user_data
        ).count()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        country_id = self.kwargs['pk']
        user_data = self.request.user
        ar_status = StatusTypeEnum.ASSESSMENT_REJECTED.value
        today_1 = datetime.now().date()
        yesterday_1 = today_1 - timedelta(days=1)
        yesterday_2 = today_1 - timedelta(days=2)

        partner_students = Student.objects.filter(partner=self.partner)
        total_rejected_assessment = partner_students.filter(is_active=True, assessment_status__name=ar_status).count()
        total_received_assessment = AssessmentRequest.objects.filter(
            student__in=partner_students,
            assessment__isnull=False,
            assessment_officer__isnull=False,
            is_active=True
        ).count()
        status_list = [
            StatusTypeEnum.APPLICATION_SUBMITTED.value,
            StatusTypeEnum.PRESCREENING_APPROVED.value
        ]

        total_student = Student.objects.filter(partner__user=user_data, study_country_id=country_id).count()
        total_applications = Application.objects.filter(student__partner__user=user_data,
                                                        student__study_country_id=country_id)
        total_application = total_applications.count()

        total_pending_assessment = AssessmentRequest.objects.filter(
            student__in=partner_students,
            assessment__isnull=True,
            assessment_officer__isnull=True,
            is_active=True
        ).count()

        status_with_application = []
        for status in self.all_statuses:
            app_count = total_applications.filter(current_status=status).count()
            status_with_application.append({'status': status, 'count': app_count})

        context['country_id'] = country_id
        context['total_student_count'] = total_student
        context['status_with_application'] = status_with_application
        context['total_application'] = total_application
        context['total_pending_assessment'] = total_pending_assessment
        context['total_received_assessment'] = total_received_assessment
        context['total_rejected_assessment'] = total_rejected_assessment
        context['today'] = today_1
        context['yesterday'] = yesterday_1
        context['yesterday2'] = yesterday_2
        context['countries'] = Country.objects.filter(is_active=True, is_active_for_university=True).order_by(
            "priority")
        context['universities'] = University.objects.filter(is_active=True, country_id=country_id).order_by("priority")[
                                  :5]
        context['webinars'] = Webinar.objects.filter(is_active=True).order_by("-created")
        context['years'] = Year.objects.current_to_future()
        context['levels'] = Level.objects.all()
        return context


class UploadPartnerDocumentView(CreateView):
    model = PartnerAgreement
    form_class = PartnerAgreementForm
    template_name = 'partner/upload_agreement.html'

    def get_success_url(self):
        messages.success(self.request, "Partner agreement uploaded!")
        return reverse('partner:docs')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        file = form.cleaned_data.get('agreement')

        # Check if the file is a PDF
        if file and not file.name.lower().endswith('.pdf'):
            messages.error(self.request, "Only PDF files are allowed.")
            return self.form_invalid(form)

        try:
            partner = Partner.objects.get(user=self.request.user)
            self.object.partner = partner
        except Partner.DoesNotExist:
            messages.error(self.request, "You are not associated with any partner.")
            return self.form_invalid(form)
        self.object.save()
        return super().form_valid(form)


class PartnerAgreementListView(ListView):
    model = PartnerAgreement
    template_name = 'partner/agreement_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(partner__user=self.request.user)
        print(queryset, 'this is queryset ')
        return queryset


class CommissionStructureListView(PartnerRequiredMixin, ListView):
    model = PartnerCommissionSetup
    template_name = 'partner/commission_structure_list.html'
    paginate_by = 20

    def get_queryset(self):
        user = self.partner
        if self.request.user.is_superuser:
            queryset = super().get_queryset().order_by('-created')
        else:
            queryset = super().get_queryset().filter(region=user.state.region).order_by('-created')
        university_name = self.request.GET.get("university_name")
        if university_name:
            queryset = queryset.filter(university__name__icontains=university_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if PartnerCommission.objects.filter(partner=self.partner):
            context['latest_commission'] = PartnerCommission.objects.filter(partner=self.partner).latest('date')
        return context


class PartnerCommissionCreateView(CreateView):
    model = PartnerCommission
    form_class = PartnerCommissionForm
    template_name = "partner/commission_form.html"

    def get_initial(self):
        initial = super().get_initial()
        partner = get_object_or_404(Partner, id=self.kwargs['partner_id'])
        user = self.request.user
        assigned_university = user.employee.assigned_universities.first()
        initial['partner'] = partner
        initial['university'] = assigned_university
        # initial['date'] = timezone.now().date()
        initial['created_by'] = user
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        partner_id = self.kwargs.get('partner_id')
        user = self.request.user
        form.create_remark(user, partner_id)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partner_id'] = self.kwargs['partner_id']
        return context

    def get_success_url(self):
        messages.success(self.request, "Commission Set Successfully!")
        if self.request.user.is_superuser:
            return reverse('paceapp:partner_list')
        else:
            return reverse('paceapp:premium_partner_list')


class PartnerCommissionUpdateView(UpdateView):
    model = PartnerCommission
    form_class = PartnerCommissionForm
    template_name = "partner/commission_form.html"

    def get_initial(self):
        initial = super().get_initial()
        partner_commission = self.get_object()
        user = self.request.user
        assigned_university = user.employee.assigned_universities.first()
        initial['partner'] = partner_commission.partner
        initial['university'] = partner_commission.university or assigned_university
        initial['date'] = partner_commission.date
        initial['created_by'] = partner_commission.created_by
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user  # Assuming you have an `updated_by` field
        partner_id = self.object.partner.id
        user = self.request.user
        form.create_remark(user, partner_id)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        partner_id = self.kwargs.get("partner_id")
        partner_commission = PartnerCommission.objects.filter(partner__id=partner_id).latest('date')
        return partner_commission

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partner_id'] = self.object.partner.id
        return context

    def get_success_url(self):
        messages.success(self.request, "Commission Updated Successfully!")
        if self.request.user.is_superuser:
            return reverse('paceapp:partner_list')
        else:
            return reverse('paceapp:premium_partner_list')


class PartnerUniversityListView(PartnerRequiredMixin, ListView):
    model = University
    template_name = "partner/university_list.html"
    CACHE_KEY = "partner_countries_with_universities"
    CACHE_TIMEOUT = 60 * 60  # 1 hour

    def get_queryset(self):
        # Attempt to retrieve cached data
        cached_data = cache.get(self.CACHE_KEY)
        university_name = self.request.GET.get('university')

        # if cached_data and not university_name:
        #     self.university_count = cached_data.get("universities_count")
        #     return cached_data.get("result")

        queryset = University.objects.filter(
            is_active=True,
            country__is_active_for_university=True
        ).select_related('country').order_by('country__priority', 'priority')

        if university_name:
            queryset = queryset.filter(name__icontains=university_name)

        # Structure data by countries
        countries_with_universities = {}
        for university in queryset:
            country = university.country
            if country not in countries_with_universities:
                countries_with_universities[country] = {
                    "country": country,
                    "universities": []
                }
            countries_with_universities[country]["universities"].append({
                "id": university.id,
                "name": university.name,
                "get_logo_url": university.get_logo_url
            })

        result = list(countries_with_universities.values())
        self.university_count = queryset.count()

        # Cache results if no search term is applied
        if not university_name:
            cache.set(
                self.CACHE_KEY,
                {"result": result, "universities_count": self.university_count},
                timeout=self.CACHE_TIMEOUT
            )

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['university_count'] = self.university_count
        context['years'] = Year.objects.current_to_future()
        context['levels'] = Level.objects.all()
        return context


class PartnerStudentListView(PartnerRequiredMixin, ListView):
    model = Student
    template_name = 'partner/student_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(partner__user=self.request.user).order_by("-created")
        country_id = self.request.GET.get('country_id')  # Get country_id from query parameters

        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        partner = self.request.GET.get('partner')
        study_country = self.request.GET.get('study_country')
        study_level = self.request.GET.get('study_level')
        status = self.request.GET.get('status')
        passport_number = self.request.GET.get('passport_number')
        filter = self.request.GET.get('filter')

        if self.request.GET.get('filter') == 'country' and country_id:
            queryset = queryset.filter(study_country_id=country_id)

        if name:
            queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if email:
            queryset = queryset.filter(email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if partner:
            queryset = queryset.filter(partner_id=partner)
        if study_country:
            queryset = queryset.filter(study_country_id=study_country)

        if study_level:
            queryset = queryset.filter(study_level_id=study_level)

        if passport_number:
            queryset = queryset.filter(passport_number__icontains=passport_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        levels = cache.get('levels')
        if not levels:
            levels = Level.objects.all()
            cache.set('levels', levels, 3600)
        context['levels'] = levels
        context['countries'] = Country.objects.filter(is_active_for_university=True)
        context['universities'] = University.objects.all()
        return context


class PartnerStudentDetailView(PartnerRequiredMixin, DetailView):
    model = Student
    template_name = 'partner/student_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        academic = None
        if self.object.study_level:
            if self.object.study_level.level == LevelEnum.UNDERGRADUATE.value:
                academic = UGStudentAcademic.objects.filter(student=self.object).first()
            elif self.object.study_level.level == LevelEnum.POSTGRADUATE.value:
                academic = PGStudentAcademic.objects.filter(student=self.object).first()
        ctx['academic'] = academic
        user = get_object_or_404(Student, id=self.object.id)
        if hasattr(user, 'employee'):
            assigned_universities = user.employee.assigned_universities.filter(is_active=True,
                                                                               country=user.study_country)
        else:
            assigned_universities = University.objects.filter(is_active=True, country=user.study_country).order_by('priority')

        # Filter applications and assessments by assigned universities
        ctx['assessments'] = self.object.get_assessments
        ctx['applications'] = self.object.get_applications
        ctx['universities'] = list(assigned_universities.values('id', 'name'))
        current_year = datetime.now().year
        upcoming_year = current_year + 1
        following_year = current_year + 2
        ctx['years'] = Year.objects.filter(is_active=True,
                                           intake_year__in=[current_year, upcoming_year, following_year])
        ctx['country_specific'] = StatusType.objects.filter(is_active=True)

        if assigned_universities.exists():
            university_id = assigned_universities.first().id
            ctx['course_api_url'] = f"/api/courses/{university_id}/"
            ctx['intake_api_url'] = f"/api/intakes/{university_id}/"
        ctx['not_send_assessment'] = not has_application_manager_permission_dashboard(self.request)
        ctx['not_apply_direct_application'] = True

        if has_assessment_permission(self.request):
            ctx['not_apply_direct_application'] = True
        else:
            if hasattr(user, 'employee') and hasattr(user.employee, 'applicationmanager'):
                app_manager = user.employee.applicationmanager
                if app_manager.is_head and app_manager.will_process_application:
                    ctx['not_apply_direct_application'] = False

        return ctx

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.partner != self.partner and not self.request.user.is_staff:
            return redirect('partner:list_student')
        return super().dispatch(request, *args, **kwargs)


class RequestedAssessmentListView(PartnerRequiredMixin, ListView):
    model = AssessmentRequest
    template_name = 'partner/requested_assessment.html'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        partner_students = Student.objects.filter(partner__user=user)
        queryset = super().get_queryset().filter(student__partner__user=user)

        student = self.request.GET.get('student')
        passport_number = self.request.GET.get('passport_number')
        university = self.request.GET.get('university')
        filter_type = self.request.GET.get('filter')

        ass_received_students = AssessmentDiscovery.objects.filter(student__in=partner_students).values('student')

        if filter_type == 'pending-assessment':
            queryset = queryset.filter(
                student__in=partner_students, assessment_officer__isnull=True,
                assessment__isnull=True, is_active=True
            ).exclude(student__in=ass_received_students).distinct('student')

        elif filter_type == 'receive-assessment':
            queryset = queryset.filter(student__in=ass_received_students, is_active=True).distinct('student')

        if student:
            queryset = queryset.filter(
                Q(student__first_name__icontains=student) | Q(student__last_name__icontains=student)
            )

        if university:
            queryset = queryset.filter(university__id=university)

        if passport_number:
            queryset = queryset.filter(student__passport_number__icontains=passport_number)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['universities'] = University.objects.all()
        ctx['filter_type'] = self.request.GET.get('filter')
        return ctx


class PartnerAssessmentListView(PartnerRequiredMixin, ListView):
    model = Student
    paginate_by = 20
    template_name = 'partner/assessment.html'

    def get_queryset(self):
        user = self.request.user
        ar_status = StatusTypeEnum.ASSESSMENT_REJECTED.value
        queryset = super().get_queryset().filter(is_active=True, partner__user=user)

        filter_type = self.request.GET.get('filter')
        if filter_type == 'rejected':
            queryset = queryset.filter(partner__user=user, assessment_status__name=ar_status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['StatusTypeEnum'] = StatusTypeEnum.ASSESSMENT_REJECTED.value
        return context


class RequestAssessmentView(PartnerRequiredMixin, BaseDetailView):
    model = Student

    def send_notifications_to_assessment_officers(self, assessment_requests):
        """Send notifications to assessment officers for the given requests."""
        student = self.object
        for ass_req_obj in assessment_requests:
            as_officer_obj = get_assessment_officer(university=ass_req_obj.university, full_details=True)
            if as_officer_obj:
                verb_msg = f"Assessment requested from {student.partner} for {ass_req_obj.university}"
                notify.send(
                    sender=self.request.user,
                    recipient=as_officer_obj.user,
                    verb=verb_msg,
                    action_object=ass_req_obj,
                    target=student
                )

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        self.object = student
        university_ids = request.POST.getlist("university")
        universities = University.objects.filter(id__in=university_ids).order_by("priority")

        if not universities.exists():
            messages.warning(request, "No valid universities selected.")
            return redirect(reverse("partner:partner_student_detail", kwargs={'pk': student.pk}))

        new_requests = []
        try:
            with transaction.atomic():
                for university in universities:
                    if not AssessmentRequest.objects.filter(student=student, university=university,
                                                            is_active=True).exists():
                        new_requests.append(AssessmentRequest(student=student, university=university))

                # Bulk create assessment requests
                if new_requests:
                    assessment_requests = AssessmentRequest.objects.bulk_create(new_requests)

                    # Notify the assessment officers for each created request
                    self.send_notifications_to_assessment_officers(assessment_requests)
                    student.assessment_requested = True
                    student.save()
                    messages.success(request, "Assessment request updated successfully!")
                    sent_mail_to_university_on_ass_request(ass_requests=assessment_requests)
                else:
                    messages.warning(request, "No assessments were requested.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            logger.error(f"Error requesting assessment for student {student.id}: {str(e)}")

        return redirect(reverse("partner:partner_student_detail", kwargs={'pk': student.pk}))


class PartnerApplicationList(ListView):
    model = Application
    template_name = 'partner/application_list.html'
    paginate_by = 20

    def get_filtered_queryset(self, status_type, user):
        return super().get_queryset().filter(
            current_status__name=status_type,
            student__partner__user=user
        )

    def get_queryset(self):
        user = self.request.user
        queryset = (super().get_queryset().filter(student__partner__user=user).select_related(
            'student__ugstudentacademic', 'student__pgstudentacademic'
        ).order_by("-created"))
        country_id = self.request.GET.get('country_id')

        student = self.request.GET.get('student')
        passport_number = self.request.GET.get('passport_number')
        university = self.request.GET.get('university')
        level = self.request.GET.get('level')
        intake = self.request.GET.get('intake')
        year = self.request.GET.get('year')
        application_status = self.request.GET.get('application_status')
        filter_type = self.request.GET.get('filter')
        filter = self.request.GET.get('status')

        if filter:
            queryset = queryset.filter(current_status__name=filter)

        status_list = [
            StatusTypeEnum.APPLICATION_SUBMITTED.value,
            StatusTypeEnum.PRESCREENING_APPROVED.value
        ]
        filter_mapping = {
            'application-pending-from-ioa': StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value,
            'application-pending-from-agent': StatusTypeEnum.APPLICATION_PENDING_FROM_AGENT.value,
            'conditional-offer': StatusTypeEnum.CONDITIONAL_OFFER_LETTER.value,
            'unconditional-offer': StatusTypeEnum.UNCONDITIONAL_OFFER_LETTER.value,
            'revised-offer-pending': StatusTypeEnum.REVISED_OFFER_PENDING.value,
            'fee-paid': StatusTypeEnum.FEE_PAID.value,
            'visa-grant': StatusTypeEnum.VISA_GRANT.value,
            'visa-lodged': StatusTypeEnum.VISA_LODGED.value,
            'visa-refused': StatusTypeEnum.VISA_REFUSED.value,
        }
        if self.request.GET.get('filter') == 'country' and country_id:
            queryset = queryset.filter(student__study_country_id=country_id)

        if filter_type in filter_mapping:
            queryset = self.get_filtered_queryset(filter_mapping[filter_type], user)

        if filter_type == 'awaited':
            queryset = queryset.filter(current_status__name__in=status_list, student__partner__user=user)

        if student:
            queryset = queryset.filter(
                Q(student__first_name__icontains=student) | Q(student__last_name__icontains=student))

        if passport_number:
            queryset = queryset.filter(student__passport_number__icontains=passport_number)

        if university:
            queryset = queryset.filter(course__university__id=university)

        if level:
            queryset = queryset.filter(course__level__id=level)

        if intake:
            queryset = queryset.filter(intake__id=intake)

        if year:
            queryset = queryset.filter(year__id=year)

        if application_status:
            queryset = queryset.filter(current_status__name__icontains=application_status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['universities'] = University.objects.all()
        context['intakes'] = Intake.objects.filter()
        context['years'] = Year.objects.all()
        levels = cache.get('levels')
        if not levels:
            levels = Level.objects.all()
            cache.set('levels', levels, 3600)
        context['levels'] = levels
        return context


class ApplicationApplyView(PartnerRequiredMixin, DetailView, FormMixin):
    model = AssessmentDiscovery
    form_class = ApplyApplicationForm
    template_name = "partner/application/apply_application.html"

    def notify_to_application_managers(self, application):
        application_manager = ApplicationManager.objects.filter(
            employee__assigned_universities=application.course.university, is_head=True
        ).first()
        if application_manager:
            verb = f"{application.student.partner} applied application for {application.course}!"
            notify.send(
                sender=self.partner.user,
                recipient=application_manager.employee.user,
                verb=verb,
                action_object=application,
                target=self.object,
            )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.initial_current_status = StatusType.objects.get(
                name=StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value
            )
        except StatusType.DoesNotExist:
            self.initial_current_status = None

    def get_initial(self):
        assessment_object = self.object
        initials = super().get_initial()
        initials['student'] = assessment_object.student
        initials['partner'] = assessment_object.student.partner
        initials['university'] = assessment_object.course.university
        initials['passport_number'] = assessment_object.student.passport_number
        initials['course'] = assessment_object.course
        initials['intake'] = assessment_object.intake
        initials['year'] = assessment_object.year
        if self.initial_current_status:
            initials['current_status'] = self.initial_current_status
        return initials

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            application = form.save(commit=False)
            application.student = self.object.student
            application.course = self.object.course
            application.year = self.object.year
            application.save()

            # Update the passport number if provided
            passport_number = form.cleaned_data.get('passport_number')
            if passport_number:
                student = self.object.student
                student.passport_number = passport_number
                student.save()
            self.object.is_processed = True
            self.object.save()
            generate_new_application_stream(
                current_user=self.request.user,
                application=application, assessment_id=self.object.id
            )
            self.notify_to_application_managers(application=application)
            messages.success(request, 'Application has been successfully applied.')
            return redirect('partner:partner_student_detail', pk=self.object.student.pk)

        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'employee'):
            kwargs['employee'] = self.request.user.employee
        return kwargs


class SetPartnerCommissionCreateView(CreateView):
    model = PartnerCommissionSetup
    form_class = SetPartnerCommissionForm
    template_name = 'partner/set_commission/_form.html'

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial['created_by'] = user
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Commission Set Successfully!")
        return reverse("partner:partner_commission_list")


class AccountManagerPartnerListView(StaffMemberRequiredMixin, ListView):
    model = Partner
    paginate_by = 20
    template_name = "dashboard/partner_account_manager/partner_list.html"

    def get_queryset(self):
        user_regions = self.request.user.employee.assigned_regions.all()
        print(user_regions, 'user_regions')
        queryset = super().get_queryset().filter(state__region__in=user_regions).order_by("-created")
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        country = self.request.GET.get('country')
        status = self.request.GET.get('status')
        mobile_number = self.request.GET.get('mobile_number')
        email_verified = self.request.GET.get("email_verified")
        agreement_uploaded = self.request.GET.get("agreement_uploaded")

        if name:
            queryset = queryset.filter(company_name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if country:
            queryset = queryset.filter(country_id=country)

        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if email_verified in ['True', 'False']:
            partner_emails = queryset.values_list('email', flat=True)
            from allauth.account.models import EmailAddress
            email_addresses = EmailAddress.objects.filter(email__in=partner_emails)
            verified_emails = email_addresses.filter(verified=email_verified).values_list('email', flat=True)
            queryset = queryset.filter(email__in=verified_emails)

        if agreement_uploaded in ["True", "False"]:
            partner_ids_with_agreements = PartnerAgreement.objects.exclude(agreement="").values_list(
                'partner_id', flat=True
            )
            if agreement_uploaded == "False":
                queryset = queryset.exclude(id__in=partner_ids_with_agreements)

            elif agreement_uploaded == "True":
                queryset = queryset.filter(id__in=partner_ids_with_agreements)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context


class PartnerAccountManagerStudentListView(ListView):
    model = Student
    paginate_by = 20
    template_name = 'dashboard/partner_account_manager/student_list.html'

    def get_queryset(self):
        user_regions = self.request.user.employee.assigned_regions.all()
        queryset = super().get_queryset().filter(partner__state__region__in=user_regions).order_by("-created")
        country_id = self.request.GET.get('country_id')

        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        partner = self.request.GET.get('partner')
        study_country = self.request.GET.get('study_country')
        study_level = self.request.GET.get('study_level')
        status = self.request.GET.get('status')
        passport_number = self.request.GET.get('passport_number')
        filter = self.request.GET.get('filter')

        if self.request.GET.get('filter') == 'country' and country_id:
            queryset = queryset.filter(study_country_id=country_id)

        if name:
            queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if email:
            queryset = queryset.filter(email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if partner:
            queryset = queryset.filter(partner_id=partner)
        if study_country:
            queryset = queryset.filter(study_country_id=study_country)

        if study_level:
            queryset = queryset.filter(study_level_id=study_level)

        if passport_number:
            queryset = queryset.filter(passport_number__icontains=passport_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        levels = cache.get('levels')
        if not levels:
            levels = Level.objects.all()
            cache.set('levels', levels, 3600)
        context['levels'] = levels
        context['countries'] = Country.objects.filter(is_active_for_university=True)
        context['universities'] = University.objects.all()
        return context
