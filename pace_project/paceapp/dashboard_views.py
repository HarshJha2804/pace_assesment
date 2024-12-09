from datetime import timedelta, datetime
from decimal import Decimal
from django.db.models import Sum
from allauth.account.models import EmailAddress
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.views.generic import TemplateView
from actstream.models import Action
from pace_project.core.mixins import RMHRequiredMixin, ASFRequiredMixin, CMPORequiredMixin, INORequiredMixin, \
    AMRequiredMixin, DMORequiredMixin, SuperuserRequiredMixin
from pace_project.core.models.application_models import Application, ApplicationStatusLog
from pace_project.core.models.core_models import StatusType, CountrySpecificStatus, AssessmentRequest
from pace_project.core.models.target_models import RMUniversityIntake, RMTarget
from pace_project.paceapp.enums import ActivityStreamVerb
from pace_project.paceapp.models import University, Course, Country, Intake, Year, AssessmentDiscovery
from pace_project.users.models import Student, Partner, PartnerAgreement
from pace_project.core.enums import StatusTypeEnum


class SuperAdminDashboardView(SuperuserRequiredMixin, TemplateView):
    """
    SuperAdmin & CEO Dashboard view.
    """
    template_name = "dashboard/super_admin/_dashboard.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.active_status = StatusType.objects.filter(is_active=True).order_by('priority')

    def get_activity_for_last_days(self, num_days):
        today = datetime.now().date()

        # Generate the list of dates dynamically
        days = [(today - timedelta(days=i)) for i in range(num_days)]
        status_logs = ApplicationStatusLog.objects.filter(
            status__in=self.active_status,
            created__date__in=days
        )
        activities = []
        for day in days:
            status_counts = []
            for status in self.active_status:
                app_count = status_logs.filter(
                    status=status,
                    created__date=day
                ).count()
                status_counts.append({'count': app_count, 'status': status})
            activities.append({'date': day, 'status_counts': status_counts})

        return activities

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # General counts
        ctx['total_partner_count'] = Partner.objects.filter().count()
        ctx['total_student_count'] = Student.objects.filter(is_active=True).count()
        ctx['total_application_count'] = Application.objects.filter(is_active=True).count()

        active_countries = Country.objects.filter(is_active=True).order_by("priority")
        country_status_list = []

        for country in active_countries:
            status_data = []

            # Get total student and application counts for the country
            total_students = Student.objects.filter(is_active=True, study_country=country).count()
            total_applications = Application.objects.filter(is_active=True, course__country=country).count()

            status_data.extend([
                {'status': 'Total Students', 'count': str(total_students)},
                {'status': 'Total Applications', 'count': str(total_applications)}
            ])

            country_specific_status = CountrySpecificStatus.objects.filter(country=country, is_active=True) \
                .prefetch_related('status_types').first()

            if country_specific_status:
                active_status_types = country_specific_status.status_types.filter(is_active=True).order_by('priority')

                for status in active_status_types:
                    status_count = Application.objects.filter(
                        current_status=status, course__country=country, is_active=True
                    ).count()
                    status_data.append({'status': status, 'count': str(status_count)})

                universities = University.objects.filter(country=country, is_active=True).only('pk', 'name', 'logo')

                country_status_list.append({
                    'country': country,
                    'statuses': status_data,
                    'universities': universities
                })

        ctx['country_status_list'] = country_status_list
        ctx['status_list'] = self.active_status
        ctx['activities'] = self.get_activity_for_last_days(3)
        return ctx


class ProjectWiseDashboardView(SuperuserRequiredMixin, TemplateView):
    template_name = "dashboard/super_admin/project_wise_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        excluded_status_types = [
            StatusTypeEnum.ASSESSMENT_SENT.value,
            StatusTypeEnum.ASSESSMENT_REJECTED.value,
        ]
        intake_id = self.request.GET.get("intake")
        year_id = self.request.GET.get("year")

        # Prefetch active universities and related statuses in a single query
        active_countries = Country.objects.filter(is_active=True, is_active_for_university=True).order_by('priority')
        active_universities = University.objects.filter(
            is_active=True, country__in=active_countries
        ).order_by('priority')

        # Prefetch statuses and optimize status fetching with related countries
        country_statuses = CountrySpecificStatus.objects.filter(
            country__in=active_countries, is_active=True
        ).prefetch_related('status_types')

        filter_conditions = {'course__university__in': active_universities}

        if intake_id:
            filter_conditions['intake_id'] = intake_id

        if year_id:
            filter_conditions['year_id'] = year_id

        # Annotate application count per status and university
        applications_per_university_status = Application.objects.filter(**filter_conditions).values(
            'course__university', 'current_status'
        ).annotate(application_count=Count('id'))

        # Prepare a dictionary to store application counts for quick lookup
        app_count_lookup = {
            (app['course__university'], app['current_status']): app['application_count']
            for app in applications_per_university_status
        }

        country_wise_university_data = []

        for country in active_countries:
            universities = active_universities.filter(country=country)
            country_status = next(
                (status for status in country_statuses if status.country == country), None
            )

            if universities and country_status and country_status.status_types.exists():
                status_types = country_status.status_types.all()
                status_types = status_types.exclude(name__in=excluded_status_types)

                status_wise_application_data = [
                    {
                        "status": status,
                        "application_counts": [
                            {
                                "university": university,
                                "count": app_count_lookup.get((university.id, status.id), 0)
                            }
                            for university in universities
                        ]
                    }
                    for status in status_types
                ]

                country_university_data = {
                    "country": country,
                    "universities": universities,
                    "statuses": status_wise_application_data,
                }
                country_wise_university_data.append(country_university_data)

        context['country_wise_university_data'] = country_wise_university_data
        context['intakes'] = Intake.objects.all()
        context['years'] = Year.objects.all().order_by('-intake_year')
        return context


class RHMDashboardView(RMHRequiredMixin, TemplateView):
    """
    Regional Marketing Head Dashboard
    """
    template_name = "dashboard/regional_marketing_head/_regional_marketing_head.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.assigned_universities = self.employee.assigned_universities.filter(is_active=True)
        self.assigned_country = self.employee.assigned_country
        self.country_specific_status = CountrySpecificStatus.objects.filter(
            country=self.assigned_country).prefetch_related('status_types')
        self.all_statuses = StatusType.objects.filter(
            country_specific_statuses__in=self.country_specific_status,
            is_active=True
        ).distinct().order_by('priority')

        self.active_intakes = RMUniversityIntake.objects.filter(rm=self.employee, is_active=True).values('intake_id')
        self.active_year = RMUniversityIntake.objects.filter(rm=self.employee, is_active=True).values('year_id')
        self.partners = RMTarget.objects.filter(rm=self.employee, intake_id__in=self.active_intakes,
                                                year_id__in=self.active_year).values_list('partner', flat=True)

    def get_activity_for_last_days(self, num_days):
        today = datetime.now().date()
        application_status = ApplicationStatusLog.objects.filter(
            application__is_active=True,
            application__student__partner__id__in=self.partners,
            application__course__university__in=self.assigned_universities
        )

        # Generate the list of dates dynamically
        days = [(today - timedelta(days=i)) for i in range(num_days)]
        status_logs = application_status.filter(
            status__in=self.all_statuses,
            created__date__in=days
        )

        activities = []
        for day in days:
            status_counts = []
            for status in self.all_statuses:
                app_count = status_logs.filter(
                    status=status,
                    created__date=day
                ).count()
                status_counts.append(app_count)
            activities.append({'date': day, 'status_counts': status_counts})
        return activities

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_1 = datetime.now().date()
        yesterday_1 = today_1 - timedelta(days=1)
        yesterday_2 = today_1 - timedelta(days=2)
        total_application = Application.objects.filter(
            is_active=True,
            student__partner__id__in=self.partners,
            course__university__in=self.assigned_universities,
            year__id__in=self.active_year,
            intake__id__in=self.active_intakes
        ).count()

        # total_pending_commission = Partner.objects.filter(
        #     Q(partner_commissions__isnull=True) | Q(partner_commissions__commission=Decimal('0.00')),
        #     id__in=self.partners,
        # ).distinct().count()

        country_specific_status = CountrySpecificStatus.objects.filter(country=self.assigned_country).first()
        achievement_status_ids = country_specific_status.achievement_statuses.filter(
            is_active=True).values_list('id', flat=True)

        total_achieved_target = Application.objects.filter(
            is_active=True,
            student__partner__id__in=self.partners,
            current_status__in=achievement_status_ids,
            course__university__in=self.assigned_universities,
            year__id__in=self.active_year,
            intake__id__in=self.active_intakes
        ).count()

        applications = Application.objects.filter(
            is_active=True,
            student__partner__id__in=self.partners,
            course__university__in=self.assigned_universities,
            year__id__in=self.active_year,
            intake__id__in=self.active_intakes
        )
        today_total_application_count = applications.filter(created__date=today_1).count()
        yesterday_total_application_count = applications.filter(created__date=yesterday_1).count()
        yesterday_2_total_application_count = applications.filter(created__date=yesterday_2).count()

        status_with_application = []
        for status in self.all_statuses:
            app_count = applications.filter(current_status=status).count()
            status_with_application.append({'status': status, 'count': app_count})

        context['status_with_application'] = status_with_application
        context['university_logos'] = self.assigned_universities
        context['total_application'] = total_application
        context['activities'] = self.get_activity_for_last_days(3)
        context['today'] = today_1
        context['yesterday'] = yesterday_1
        context['yesterday_2'] = yesterday_2

        context['today_total_application_count'] = today_total_application_count
        context['yesterday_total_application_count'] = yesterday_total_application_count
        context['yesterday_2_total_application_count'] = yesterday_2_total_application_count
        context['total_achieved_target'] = total_achieved_target
        context['intakes'] = self.active_intakes.values_list(
            'intake__intake_month', flat=True).distinct()
        total_target = self.partners.aggregate(total_target=Sum('target'))['total_target'] or 0
        context['total_target'] = total_target
        context['total_balance'] = total_target - total_achieved_target

        return context


class AssessmentOfficerDashboardView(ASFRequiredMixin, TemplateView):
    template_name = 'paceapp/dashboard/assessment_officer_dashboard/_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user_data = self.request.user.id
        today_1 = datetime.now().date()
        yesterday_1 = today_1 - timedelta(days=1)
        yesterday_2 = today_1 - timedelta(days=2)

        assigned_universities = self.employee.assigned_universities.all()

        # Retrieve students who have received assessments for assigned universities
        received_students = AssessmentDiscovery.objects.filter(
            course__university__in=assigned_universities
        ).values_list("student", flat=True)

        # Calculate total assessments requested for assigned universities
        total_assessments = AssessmentRequest.objects.filter(
            university__in=assigned_universities
        ).count()

        # Calculate total sent assessments (active assessments sent to received students)
        total_sent_assessments = AssessmentRequest.objects.filter(
            student__in=received_students, is_active=True, university__in=assigned_universities
        ).count()

        # Calculate total pending assessments (active, unassigned assessments not sent to received students)
        total_pending_assessments = AssessmentRequest.objects.filter(
            university__in=assigned_universities, is_active=True, assessment_officer__isnull=True
        ).exclude(student__in=received_students).count()

        # Calculate total rejected assessments (inactive assessments)
        total_rejected_assessments = AssessmentRequest.objects.filter(
            is_active=False, university__in=assigned_universities
        ).count()

        context.update({
            "total_assessments": total_assessments,
            "total_sent_assessments": total_sent_assessments,
            "total_pending_assessments": total_pending_assessments,
            "total_rejected_assessments": total_rejected_assessments,
        })

        total_assessments = Action.objects.filter(
            actor_object_id=user_data, verb=ActivityStreamVerb.TOTAL_ASSESSMENT.value
        )
        sent_assessments = Action.objects.filter(
            actor_object_id=user_data, verb=ActivityStreamVerb.SENT_ASSESSMENT.value
        )
        rejected_assessments = Action.objects.filter(
            actor_object_id=user_data, verb=ActivityStreamVerb.REJECTED_ASSESSMENT.value
        )

        context['today_1'] = today_1
        context['yesterday_1'] = yesterday_1
        context['yesterday_2'] = yesterday_2

        # Today’s counts
        context["today_total_assessment"] = total_assessments.filter(timestamp__date=today_1).count()
        context['today_sent_assessment'] = sent_assessments.filter(timestamp__date=today_1).count()
        context['today_rejected_assessment'] = rejected_assessments.filter(timestamp__date=today_1).count()

        # Yesterday’s counts
        context['yesterday_total_assessment'] = total_assessments.filter(timestamp__date=yesterday_1).count()
        context['yesterday_sent_assessment'] = sent_assessments.filter(timestamp__date=yesterday_1).count()
        context['yesterday_rejected_assessment'] = rejected_assessments.filter(timestamp__date=yesterday_1).count()

        # Day before yesterday’s counts
        context['yesterday_2_total_assessment'] = total_assessments.filter(timestamp__date=yesterday_2).count()
        context['yesterday_2_sent_assessment'] = sent_assessments.filter(timestamp__date=yesterday_2).count()
        context['yesterday_2_rejected_assessment'] = rejected_assessments.filter(timestamp__date=yesterday_2).count()
        return context


class AMDashboardView(AMRequiredMixin, TemplateView):
    template_name = "dashboard/application_manager/_dashboard_application_manager.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.employee:
            if not self.employee.applicationmanager:
                return redirect("paceapp:home")
        else:
            return redirect("paceapp:home")

        self.is_head = self.employee.applicationmanager.is_head
        status_names = [
            StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value,
            StatusTypeEnum.APPLICATION_PENDING_FROM_AGENT.value,
            StatusTypeEnum.APPLICATION_SUBMITTED.value,
            StatusTypeEnum.PRESCREENING_PENDING.value
        ]
        self.active_status = StatusType.objects.filter(name__in=status_names).order_by('priority')
        self.assigned_country = self.employee.assigned_country
        self.assigned_universities = self.employee.assigned_universities.all()
        self.applications_queryset = Application.objects.filter(
            is_active=True, course__country=self.assigned_country
        )

    def get_total_applications_count(self):
        applications = self.applications_queryset
        if self.is_head:
            return applications.filter(course__university__in=self.assigned_universities).count()
        return applications.filter(application_manager=self.employee.user).count()

    def get_unassigned_count(self):
        if self.is_head:
            return self.applications_queryset.filter(
                course__university__in=self.assigned_universities,
                application_manager__isnull=True
            ).count()
        return 0

    def get_status_counts(self):
        status_data = []
        for status in self.active_status:
            filters = {
                'current_status': status,
                'course__country': self.assigned_country,
                'is_active': True,
            }
            if self.is_head:
                filters['course__university__in'] = self.assigned_universities
            else:
                filters['application_manager'] = self.employee.user

            count = self.applications_queryset.filter(**filters).count()
            status_data.append({'status': status, 'count': str(count)})
        return status_data

    def get_activity_for_last_days(self, num_days):
        today = datetime.now().date()

        # Generate the list of dates dynamically
        days = [(today - timedelta(days=i)) for i in range(num_days)]

        status_logs = ApplicationStatusLog.objects.filter(
            status__in=self.active_status,
            created__date__in=days
        )
        if self.is_head:
            status_logs = status_logs.filter(
                application__course__university__in=self.employee.assigned_universities.all())
        else:
            status_logs = status_logs.filter(application__application_manager=self.employee.user)

        activities = []
        for day in days:
            status_counts = []
            for status in self.active_status:
                app_count = status_logs.filter(
                    status=status,
                    created__date=day
                ).count()
                status_counts.append(app_count)
            activities.append({'date': day, 'status_counts': status_counts})

        return activities

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        status_data = [{'status': 'Total Applications', 'count': str(self.get_total_applications_count())}, ]
        # if self.is_head:
        #     status_data.append({'status': 'Unassigned Application Manager', 'count': str(self.get_unassigned_count())})
        ctx['status_list'] = self.active_status
        ctx['activities'] = self.get_activity_for_last_days(3)
        ctx['status_data'] = status_data + self.get_status_counts()
        # ctx['is_head'] = self.is_head
        return ctx


class INODashboardView(INORequiredMixin, TemplateView):
    """
    Interview Officer Dashboard
    """
    template_name = "dashboard/interview_officer/_interview_officer.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        interview_status_ids = self.get_interview_statuses()
        interview_status_types = StatusType.objects.filter(id__in=interview_status_ids).order_by('priority')

        # Aggregate application counts by status
        application_counts = (
            Application.objects.filter(current_status_id__in=interview_status_ids)
            .values('current_status')
            .annotate(count=Count('id'))
        )

        # Map counts to statuses
        status_application_counts = {
            status['current_status']: status['count'] for status in application_counts
        }

        # Prepare data for context
        ctx['status_with_application_counts'] = [
            {
                "status": status.name,
                "application_count": status_application_counts.get(status.id, 0)
            }
            for status in interview_status_types
        ]
        return ctx


class CMPODashboardView(CMPORequiredMixin, TemplateView):
    template_name = "dashboard/compliance_officer/_compliance_officer.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.assigned_universities = self.employee.assigned_universities.filter(is_active=True)
        self.assigned_country = self.employee.assigned_country
        self.country_specific_status = CountrySpecificStatus.objects.filter(
            country=self.assigned_country).prefetch_related('status_types')
        self.all_statuses = StatusType.objects.filter(
            country_specific_statuses__in=self.country_specific_status,
            is_active=True
        ).distinct().order_by('priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status_with_compliance = []

        excluded_statuses = {
            StatusTypeEnum.ASSESSMENT_SENT.value,
            StatusTypeEnum.ASSESSMENT_REJECTED.value
        }

        total_applications = Application.objects.filter(
            is_active=True,
            course__country=self.employee.assigned_country,
            course__university__in=self.employee.assigned_universities.all()
        ).exclude(current_status__name__in=excluded_statuses).count()

        for status in self.all_statuses:
            if status.name in excluded_statuses:
                continue
            app_count = Application.objects.filter(
                current_status=status,
                is_active=True,
                course__country=self.assigned_country,
                course__university__in=self.assigned_universities.all()
            ).count()

            status_with_compliance.append({
                'status_name': status.name,
                'label': status.name,
                'count': app_count,
            })

        context['status_with_compliance'] = status_with_compliance
        context['total_applications'] = total_applications

        # --- 3-Day Activity Tracking ---
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)

        def get_application_counts_by_day(day):
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())

            return {
                'total_applications': Application.objects.filter(
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).exclude(current_status__name__in=excluded_statuses).count(),
                'submitted_status': Application.objects.filter(
                    current_status__name='Application Submitted',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'rejected_status': Application.objects.filter(
                    current_status__name='Rejected By IG',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'conditional_offer_letter_status': Application.objects.filter(
                    current_status__name='Conditional Offer Received',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'unconditional_offer_letter_status': Application.objects.filter(
                    current_status__name='Unconditional Offer Received',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'fee_paid_status': Application.objects.filter(
                    current_status__name='Fee Paid',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'coe_applied_status': Application.objects.filter(
                    current_status__name='COE Applied',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'coe_received_status': Application.objects.filter(
                    current_status__name='COE Received',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'visa_lodged_status': Application.objects.filter(
                    current_status__name='VISA Lodged',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'visa_grant_status': Application.objects.filter(
                    current_status__name='VISA Grant',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
                'visa_refused_status': Application.objects.filter(
                    current_status__name='VISA Refused',
                    created__range=(day_start, day_end),
                    is_active=True,
                    course__country=self.assigned_country,
                    course__university__in=self.assigned_universities.all()
                ).count(),
            }

        context['today_1'] = today
        context['yesterday_1'] = yesterday
        context['yesterday_2'] = day_before_yesterday

        context['today'] = get_application_counts_by_day(today)
        context['yesterday'] = get_application_counts_by_day(yesterday)
        context['day_before_yesterday'] = get_application_counts_by_day(day_before_yesterday)

        return context


class DataManagementOfficerDashboard(DMORequiredMixin, TemplateView):
    template_name = 'paceapp/dashboard/data_management_officer_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user_data = self.request.user.id
        today_1 = datetime.now().date()
        yesterday_1 = today_1 - timedelta(days=1)
        yesterday_2 = today_1 - timedelta(days=2)

        active_country_for_university = Country.objects.filter(is_active_for_university=True).count()
        active_country_for_student = Country.objects.filter(is_active_for_student=True).count()
        total_project = University.objects.all().count()
        active_project = University.objects.filter(is_active=True).count()
        inactive_project = University.objects.filter(is_active=False).count()
        premium_project = University.objects.filter(is_premium=True).count()
        total_course = Course.objects.all().count()
        active_course = Course.objects.filter(is_active=True).count()
        inactive_course = Course.objects.filter(is_active=False).count()
        context['active_country_for_university'] = active_country_for_university
        context['active_country_for_student'] = active_country_for_student
        context['total_project'] = total_project
        context['active_project'] = active_project
        context['inactive_project'] = inactive_project
        context['premium_project'] = premium_project
        context['total_course'] = total_course
        context['active_course'] = active_course
        context['inactive_course'] = inactive_course

        return context


class VicePresidentDashboard(TemplateView):
    template_name = "dashboard/vicepresident_dashboard/_dashboard.html"


class PartnerOnBoardingOfficerDashboard(TemplateView):
    template_name = "dashboard/partner_onboarding_officer_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partners = Partner.objects.all()

        # Count active and inactive partners
        active_partners_count = partners.filter(is_active=True).count()
        inactive_partners_count = partners.filter(is_active=False).count()

        # Email verification status for partners
        partner_emails = partners.values_list('email', flat=True)
        email_addresses = EmailAddress.objects.filter(email__in=partner_emails)
        verified_email_count = email_addresses.filter(verified=True).count()
        unverified_email_count = email_addresses.filter(verified=False).count()

        # Agreement status for partners
        # agreement_uploaded_count = PartnerAgreement.objects.filter(partner__in=partners).exclude(agreement="").count()

        agreement_not_uploaded_count = partners.exclude(
            id__in=PartnerAgreement.objects.values_list('partner_id', flat=True)
        ).count()

        # Agreement status for partners
        # Case 1: Partner tried to upload but no agreement file exists
        agreement_entry_no_file_count = PartnerAgreement.objects.filter(partner__in=partners, agreement="").count()

        # Case 2: No attempt to upload (no entry in PartnerAgreement)
        no_agreement_entry_count = partners.exclude(
            id__in=PartnerAgreement.objects.values_list('partner_id', flat=True)).count()

        # Case: Agreement successfully uploaded
        agreement_uploaded_count = PartnerAgreement.objects.filter(partner__in=partners).exclude(agreement="").count()

        # Add data to context
        context.update({
            "all_partners_count": partners.count(),
            'active_partners_count': active_partners_count,
            'inactive_partners_count': inactive_partners_count,
            'verified_email_count': verified_email_count,
            'unverified_email_count': unverified_email_count,
            'agreement_uploaded_count': agreement_uploaded_count,
            'agreement_not_uploaded_count': agreement_not_uploaded_count,
        })

        return context
