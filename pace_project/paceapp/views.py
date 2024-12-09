from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView, ListView

from django.contrib import messages
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin
from notifications.models import Notification

from pace_project.core.enums import StatusTypeEnum
from pace_project.core.mixins import ASFRequiredMixin
from pace_project.core.models.core_models import StatusType, AssessmentRequest
from pace_project.core.models.generic_models import GenericRemark, GenericDocument
from pace_project.core.models.application_models import Application, ApplicationRemark
from pace_project.paceapp.actstream import reject_assessment, total_assessment, generate_new_application_stream
from pace_project.paceapp.enums import LevelEnum, RoleEnum
from pace_project.paceapp.forms import GenericDocumentForm
from pace_project.paceapp.selectors import get_student_object, get_student_academics, get_assessment_discoveries

from pace_project.paceapp.models import University, Course, UniversityStateMapping, Board, EnglishTestType, \
    Year, AssessmentDiscovery
from pace_project.paceapp.filters import filter_universities, filter_courses, filter_pg_courses, \
    filter_universities_by_student, filter_ug_courses_by_student, filter_pg_courses_by_student
from pace_project.paceapp.services import add_course_entry_criteria, add_course_english_test, \
    add_pg_course_entry_criteria, record_discovered_assessments, save_ug_student_academics, save_pg_student_academics, \
    process_assessments, update_student_assessment_status
from pace_project.paceapp.utils import handle_feedback, validate_assessment_input
from pace_project.users.models import Student, UGStudentAcademic, PGStudentAcademic


def account_signup_url_redirect_view(request):
    return redirect("partner:register")


class HomeView(TemplateView):
    template_name = 'paceapp/home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect('paceapp:super_admin_dashboard')
        elif request.user.is_authenticated:
            user_role = request.user.role.name
            if user_role == RoleEnum.ASSESSMENT_OFFICER.value:
                return redirect('paceapp:assessment_dashboard')
            elif user_role == RoleEnum.APPLICATION_MANAGER.value:
                return redirect('paceapp:dashboard_application_manager')
            elif user_role == RoleEnum.REGIONAL_MARKETING_HEAD.value:
                return redirect('paceapp:dashboard_regional_marketing_head')
            elif user_role == RoleEnum.INTERVIEW_OFFICER.value:
                return redirect('paceapp:dashboard_interview_officer')
            elif user_role == RoleEnum.DATA_MANAGEMENT_OFFICER.value:
                return redirect("paceapp:data_management_officer")
            elif user_role == RoleEnum.COMPLIANCE_OFFICER.value:
                return redirect("paceapp:dashboard_compliance_officer")
            elif user_role == RoleEnum.PARTNER_ONBOARDING_OFFICER.value:
                return redirect("paceapp:dashboard_partner_onboarding_officer")
            elif user_role == RoleEnum.PARTNER.value:
                return redirect("partner:university_list")
            elif user_role == RoleEnum.VICE_PRESIDENT.value:
                return redirect("paceapp:dashboard_vice_president")
            else:
                return super().dispatch(request, *args, **kwargs)


def notification_redirect_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if notification.target and notification.target.get_notification_url(user=request.user):
        return redirect(notification.target.get_notification_url(user=request.user))
    try:
        if notification.actor and notification.actor.get_notification_url(user=request.user):
            return redirect(notification.actor.get_notification_url(user=request.user))
    except:
        if notification.action_object and notification.action_object.get_notification_url(user=request.user):
            return redirect(notification.action_object.get_notification_url(user=request.user))

    return redirect('users:redirect')


def notification_details_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    context = {'notification': notification}
    return render(request, "notification/detail.html", context)


class UniversityDeleteView(DeleteView):
    model = University

    def get_success_url(self):
        messages.success(self.request, 'University successfully updated!')
        return reverse("paceapp:university_list")


def add_course_requirements_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.level.level == LevelEnum.POSTGRADUATE.value:
        messages.warning(request, "Please provide the course level specific requirements!")
        return redirect("paceapp:add_pg_course_requirements", pk=course.pk)

    unique_uniset = UniversityStateMapping.objects.filter(university=course.university, is_active=True)

    distinct_board_ids = unique_uniset.values('boards').distinct()
    unique_boards_queryset = Board.objects.filter(pk__in=distinct_board_ids)

    if request.method == "POST":
        form_data = request.POST
        criteria_feedback = add_course_entry_criteria(course=course, form_data=form_data)
        test_feedback = add_course_english_test(course=course, form_data=form_data)

        handle_feedback(request, criteria_feedback)
        handle_feedback(request, test_feedback)

        return redirect(course.get_absolute_url)

    context = {
        'course': course,
        'countries': course.university.application_accepting_from.all(),
        'boards': unique_boards_queryset,
        'test_types': EnglishTestType.objects.filter(is_active=True),
    }
    return render(request, "paceapp/university/course_requirements_form.html", context)


def add_pg_course_requirements_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.level.level == LevelEnum.UNDERGRADUATE.value:
        messages.warning(request, "Please provide the course level specific requirements!")
        return redirect("paceapp:add_course_requirements", pk=course.pk)

    unique_uniset = UniversityStateMapping.objects.filter(university=course.university, is_active=True)

    distinct_board_ids = unique_uniset.values('boards').distinct()
    unique_boards_queryset = Board.objects.filter(pk__in=distinct_board_ids)

    if request.method == "POST":
        form_data = request.POST
        criteria_feedback = add_pg_course_entry_criteria(course=course, form_data=form_data)
        test_feedback = add_course_english_test(course=course, form_data=form_data)

        handle_feedback(request, criteria_feedback)
        handle_feedback(request, test_feedback)

        return redirect(course.get_absolute_url)

    context = {
        'course': course,
        'countries': course.university.application_accepting_from.all(),
        'boards': unique_boards_queryset,
        'test_types': EnglishTestType.objects.filter(is_active=True),
    }
    return render(request, 'paceapp/university/pg_course_requirements_form.html', context)


def discover_assessment_view(request):
    param_student_id = request.GET.get('student_id')
    if param_student_id is not None:
        student = get_student_object(student_id=param_student_id)
        if student:
            student_academics = get_student_academics(student=student)
            if student_academics:
                universities = filter_universities_by_student(student_academic=student_academics)
                courses = filter_ug_courses_by_student(
                    valid_universities=universities, student_academic=student_academics
                )
                ass_discoveries = get_assessment_discoveries(student=student)
                context = {
                    'courses': courses,
                    'universities': universities,
                    'student_id': student.id,
                    'ass_discoveries': ass_discoveries
                }
                return render(request, 'paceapp/assessment/courses_result.html', context)

    if request.method == "POST":
        form_data = request.POST
        student_id = request.POST.get('student_id')

        if student_id != 'None':
            student = get_object_or_404(Student, pk=student_id)
            student_academics = UGStudentAcademic.objects.filter(student=student).exists()
            if not student_academics:
                # Save UG student academic details for further assessment discoveries!
                save_ug_student_academics(student=student, form_data=form_data)
                messages.success(request, "System saved student academic details!")

        filtered_universities = filter_universities(form_data=form_data)
        filtered_courses = filter_courses(valid_universities=filtered_universities, form_data=form_data)

        messages.success(request, 'Assessment discovered!')
        ctx = {'courses': filtered_courses, 'universities': filtered_universities, 'student_id': student_id}
        return render(request, 'paceapp/assessment/courses_result.html', ctx)

    context = {
        'years': Year.objects.all(),
        'student_id': param_student_id,
    }
    return render(request, 'paceapp/assessment/_form.html', context)


def discover_pg_assessment_view(request):
    param_student_id = request.GET.get('student_id')

    if param_student_id is not None:
        student = get_student_object(student_id=param_student_id)
        if student:
            student_academics = get_student_academics(student=student)
            if student_academics:
                universities = filter_universities_by_student(student_academic=student_academics)
                courses = filter_pg_courses_by_student(
                    valid_universities=universities, student_academic=student_academics
                )
                ass_discoveries = get_assessment_discoveries(student=student)
                context = {
                    'courses': courses,
                    'universities': universities,
                    'student_id': student.id,
                    'ass_discoveries': ass_discoveries
                }
                return render(request, 'paceapp/assessment/courses_result.html', context)

    if request.method == "POST":
        form_data = request.POST
        student_id = request.POST.get('student_id')
        if student_id != 'None':
            student = get_object_or_404(Student, pk=student_id)
            student_academics = PGStudentAcademic.objects.filter(student=student).exists()
            if not student_academics:
                # Save PG student academic details for further assessment discoveries!
                save_pg_student_academics(student=student, form_data=form_data)
                messages.success(request, "System saved student academic details!")

        universities = filter_universities(form_data=form_data)
        courses = filter_pg_courses(valid_universities=universities, form_data=form_data)
        context = {'courses': courses, 'universities': universities, 'student_id': student_id}
        return render(request, 'paceapp/assessment/courses_result.html', context)

    context = {
        'years': Year.objects.all(),
        'student_id': param_student_id,
    }
    return render(request, 'paceapp/assessment/_pg_form.html', context)


def save_discovered_assessments_view(request):
    if request.method == "POST":
        course_ids = request.POST.getlist('course_id')
        student_id = request.POST.get('student_id')
        if not student_id or not course_ids:
            messages.error(request, 'Invalid save assessment request!')
            return redirect("paceapp:student_list")

        filtered_courses = Course.objects.filter(id__in=course_ids)
        record_discovered_assessments(student_id=student_id, courses=filtered_courses)
        messages.success(request, 'Assessment saved!')
        return redirect(reverse('paceapp:student_detail', kwargs={'pk': student_id}))
    return HttpResponse('Invalid method!')


class DiscoveredASResultView(TemplateView):
    """
    DiscoveredAsResultView to view designing of courses result page.
    """

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['courses'] = Course.objects.filter(is_active=True)
        ctx['universities'] = University.objects.filter(is_active=True)
        return ctx

    template_name = "paceapp/assessment/courses_result.html"


def save_assessments_view(request, pk):
    student_instance = get_object_or_404(Student, pk=pk)
    user = request.user
    if request.method == 'POST':
        course_ids = request.POST.getlist('course')
        intake_ids = request.POST.getlist('intake')
        year_ids = request.POST.getlist('year')
        remark = request.POST.get('remark')

        if not validate_assessment_input(course_ids, intake_ids, year_ids):
            messages.error(request, "Please provide course, intake, and year for all entries.")
            return redirect('paceapp:student_list', pk=pk)

        process_assessments(
            student=student_instance, user=user, course_ids=course_ids,
            intake_ids=intake_ids, year_ids=year_ids, remark=remark
        )
        update_student_assessment_status(
            request=request, student=student_instance, status=StatusTypeEnum.ASSESSMENT_SENT.value
        )
        messages.success(request, "Assessment Send Successfully!")

    context = {
        'student': student_instance,
    }
    return render(request, 'paceapp/student/assessment_detail.html', context)


def mark_student_status_reject_view(request, pk):
    student_instance = get_object_or_404(Student, pk=pk)
    user_instance = request.user
    if request.method == 'POST':
        remark = request.POST.get('remark')
        if not remark:
            messages.error(request, "Please provide a remark.")
            return redirect('paceapp:student_list', pk=pk)

        # Create the ApplicationRemark
        GenericRemark.objects.create(
            content_object=student_instance,
            remark=remark,
            created_by=user_instance,

        )
        # Update the student's status to "Assessment Rejected"
        assessment_rejected_status = StatusType.objects.get(name="Assessment Rejected")
        student_instance.assessment_status = assessment_rejected_status
        student_instance.save()
        reject_assessment(user_instance, student_instance)
        total_assessment(user_instance, student_instance)
        messages.success(request, "Assessment rejected and remark saved successfully!")
        return redirect('paceapp:student_detail', pk=pk)  # Adjust to the appropriate redirect
    context = {
        'student': student_instance,
    }
    return render(request, 'paceapp/student/assessment_detail.html', context)


def save_application_view(request, pk):
    student_instance = get_object_or_404(Student, pk=pk)
    try:
        default_status = StatusType.objects.get(name="Pending From IG")
    except StatusType.DoesNotExist:
        messages.success(request, "status is not found!!")
        return redirect(student_instance.get_absolute_url)
    if request.method == 'POST':
        courses = request.POST.getlist('course')
        intakes = request.POST.getlist('intake')
        years = request.POST.getlist('year')
        remark = request.POST.get('remark')
        user_instance = request.user
        if not (courses and intakes and years):
            messages.error(request, "Please provide course, intake, and year for all entries.")
            return redirect('paceapp:student_list', pk=pk)

        for course, intake, year in zip(courses, intakes, years):
            app_object = Application.objects.create(
                student=student_instance,
                course_id=course,
                intake_id=intake,
                year_id=year,
                current_status=default_status,
            )
            GenericRemark.objects.create(
                content_object=student_instance,
                remark=remark,
                created_by=user_instance,

            )
            if app_object:
                generate_new_application_stream(
                    current_user=request.user,
                    application=app_object, is_direct=True
                )
        messages.success(request, "Application Send Successfully!")
    return redirect(student_instance.get_absolute_url)


class UploadStudentDocumentView(DetailView, FormMixin):
    model = Student
    form_class = GenericDocumentForm
    template_name = "paceapp/student/document_upload_form.html"

    def get_initial(self):
        initials = super().get_initial()
        document_types = self.object.get_document_types
        if document_types:
            initials['document_type'] = document_types
        return initials

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            if self.document_already_uploaded(form):
                return self.form_invalid(form)
            instance = form.save(commit=False)
            instance.created_by = self.request.user
            instance.content_object = self.object
            instance.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, "Document uploaded successfully!")
        return self.object.get_absolute_url

    def document_already_uploaded(self, form):
        document_type = form.cleaned_data.get("document_type")
        file = form.cleaned_data.get("file")

        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
        if file and not file.name.lower().endswith(tuple(allowed_extensions)):
            messages.error(self.request,
                           "Only files with the following extensions are allowed: PDF, DOC, DOCX, JPG, PNG.")
            return self.form_invalid(form)

        content_type = ContentType.objects.get_for_model(self.object)
        if document_type and content_type:
            if GenericDocument.objects.filter(
                object_id=self.object.id,
                content_type=content_type,
                document_type=document_type,
                is_active=True
            ).exists():
                form.add_error(
                    "document_type",
                    f"A document '{document_type}' is already uploaded for {self.object}!"
                )
                return True

        return False


class AORequestedAssessmentListView(ASFRequiredMixin, ListView):
    model = AssessmentRequest
    template_name = 'paceapp/dashboard/assessment_officer_dashboard/assessment_request.html'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(
            assessment__isnull=True, assessment_officer__isnull=True, is_active=True,
            university__in=user.employee.assigned_universities.all()).order_by('-created')

        student = self.request.GET.get('student')
        passport_number = self.request.GET.get('passport_number')
        university = self.request.GET.get('university')

        if student:
            queryset = queryset.filter(
                Q(student__first_name__icontains=student) | Q(student__last_name__icontains=student))
        if university:
            queryset = queryset.filter(university__id=university)
        if passport_number:
            queryset = queryset.filter(student__passport_number__icontains=passport_number)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['universities'] = University.objects.filter(is_active=True)
        return ctx
