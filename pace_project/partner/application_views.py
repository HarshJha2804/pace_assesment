from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.generic.edit import FormMixin

from pace_project.core.enums import StatusTypeEnum
from pace_project.core.models.application_models import Application, ApplicationRemark
from pace_project.core.models.core_models import StatusType
from pace_project.core.models.generic_models import GenericRemark, GenericDocument
from pace_project.paceapp.actstream import generate_new_application_stream
from pace_project.paceapp.enums import LevelEnum
from pace_project.paceapp.models import Course
from pace_project.partner.forms import StudentCreateForm, PartnerGenericDocumentForm
from pace_project.partner.mixins import PartnerRequiredMixin
from pace_project.partner.notifications import notify_application_manager
from pace_project.partner.services import is_valid_application_parameters, create_application, \
    is_application_already_applied
from pace_project.partner.views import logger
from pace_project.users.models import Student, Partner, UGStudentAcademic, PGStudentAcademic
from pace_project.utils.utils import get_status_object


class ApplicationDetailView(PartnerRequiredMixin, DetailView):
    model = Application
    template_name = "partner/application/_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.student.partner != self.request.user.partner and not self.request.user.is_staff:
            return redirect('partner:application_list')
        return super().dispatch(request, *args, **kwargs)


class PartnerStudentCreateView(PartnerRequiredMixin, CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = "partner/student_create_form.html"

    def setup(self, request, *args, **kwargs):
        """Initialize view-specific attributes based on query parameters."""
        super().setup(request, *args, **kwargs)
        self.passport_num = request.GET.get('passport_number')
        self.intake_id = request.GET.get('intake_id')
        self.year_id = request.GET.get('year_id')
        self.course_id = request.GET.get('course_id')
        self.current_status = get_status_object(StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value)
        self.course = None  # Course object will be fetched based on `course_id`

    def get_initial(self):
        """Provide initial data for the form based on query parameters."""
        initials = super().get_initial()

        if self.passport_num:
            initials['passport_number'] = self.passport_num

        if self.course_id:
            try:
                self.course = Course.objects.select_related('university__country').get(id=self.course_id)
                initials['study_level'] = self.course.level
                initials['study_country'] = self.course.university.country
            except Course.DoesNotExist:
                logger.error(f"Invalid course ID: {self.course_id}")
                messages.error(self.request, "Invalid course ID provided.")

        return initials

    def get_form_kwargs(self):
        """Add user instance to form kwargs for additional validation or customization."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Save the student instance and handle partner association and academics."""
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user

        # Associate student with the partner
        try:
            partner = Partner.objects.get(user=self.request.user)
            self.object.partner = partner
        except Partner.DoesNotExist:
            messages.error(self.request, "Your profile not associated with any partner instance.")
            return self.form_invalid(form)

        self.object.save()

        # Handle academic level-specific logic
        self._handle_academic_level(form.cleaned_data)

        return super().form_valid(form)

    def _handle_academic_level(self, cleaned_data):
        """Create academic records based on study level."""
        study_level = cleaned_data.get('study_level')
        country_on_passport = cleaned_data.get('country_on_passport')

        if study_level:
            if study_level.level == LevelEnum.UNDERGRADUATE.value:
                UGStudentAcademic.objects.get_or_create(student=self.object, country=country_on_passport)
            elif study_level.level == LevelEnum.POSTGRADUATE.value:
                PGStudentAcademic.objects.get_or_create(student=self.object, country=country_on_passport)

    def apply_application(self):
        """Apply an application for the student if valid parameters are provided."""
        if is_valid_application_parameters(course_id=self.course_id, intake_id=self.intake_id, year_id=self.year_id):
            if self.current_status:
                return create_application(
                    student=self.object, status=self.current_status, course_id=self.course_id,
                    intake_id=self.intake_id, year_id=self.year_id
                )
        return None

    def get_success_url(self):
        """Redirect to the success URL and handle post-creation logic."""
        messages.success(self.request, "Student added successfully!")

        if self.course:
            application = self.apply_application()
            if application:
                notify_application_manager(application=application)
                success_message = f"Application successfully applied to {application.course.university.name}."
                messages.success(self.request, success_message)
            else:
                messages.warning(self.request, "Failed to apply the application.")

        return self.object.get_student_absolute_url


class PartnerStudentUpdateView(UpdateView):
    model = Student
    form_class = StudentCreateForm
    template_name = 'partner/student_create_form.html'

    def get_success_url(self):
        messages.success(self.request, "Student updated successfully!")
        return reverse('partner:list_student')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        study_level = form.cleaned_data.get('study_level')
        country_on_passport = form.cleaned_data.get('country_on_passport')

        if study_level:
            if study_level.level == LevelEnum.UNDERGRADUATE.value:
                UGStudentAcademic.objects.update_or_create(
                    student=self.object,
                    defaults={'country': country_on_passport}
                )
            elif study_level.level == LevelEnum.POSTGRADUATE.value:
                PGStudentAcademic.objects.update_or_create(
                    student=self.object,
                    defaults={'country': country_on_passport}
                )
        return super().form_valid(form)


class PartnerUploadStudentDocumentView(DetailView, FormMixin):
    model = Student
    form_class = PartnerGenericDocumentForm
    template_name = "partner/document_upload_form.html"

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
        return self.object.get_student_absolute_url

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


def create_student_application_view(request, pk):
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
            return redirect('partner:list_student', pk=pk)

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
                notify_application_manager(application=app_object)
        messages.success(request, "Application Send Successfully!")
    return redirect(student_instance.get_student_absolute_url)


def apply_application_from_university_view(request):
    if request.method == "POST":
        intake_id = request.POST.get("intake")
        year_id = request.POST.get("year")
        course_id = request.POST.get("course")
        passport_num = request.POST.get("passport_number")

        if passport_num and course_id and intake_id:
            course = Course.objects.get(id=course_id)
            partner = request.user.partner
            is_exists = Student.objects.filter(
                partner=partner,
                passport_number__iexact=passport_num,
                study_country=course.university.country
            ).exists()

            if is_exists:
                student = Student.objects.filter(
                    partner=partner,
                    passport_number__iexact=passport_num,
                    study_country=course.university.country
                ).first()
                if is_application_already_applied(student=student, course_id=course_id, intake_id=intake_id,
                                                  year_id=year_id):
                    messages.error(request, f"Application already applied of {student}")
                    return redirect("partner:university_list")
                current_status = get_status_object(StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value)
                if is_valid_application_parameters(course_id=course_id, intake_id=intake_id, year_id=year_id):
                    if current_status:
                        application = create_application(
                            student=student, status=current_status,
                            course_id=course_id, intake_id=intake_id, year_id=year_id
                        )
                        notify_application_manager(application=application)
                        messages.success(request, 'Application has been successfully applied.')
                        return redirect('partner:partner_student_detail', pk=student.pk)
                messages.warning(request, "Failed to apply application!")
                return redirect("partner:university_list")
            else:
                create_student_url = reverse('partner:create_student')
                url_with_params = f"{create_student_url}?passport_number={passport_num}&course_id={course.id}&intake_id={intake_id}&year_id={year_id}"
                return redirect(url_with_params)
        messages.info(request, "Please first add the student!")
        return redirect("partner:create_student")


def chat_with_team_view(request, pk):
    app_instance = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        message = request.POST.get("message")
        logged_in_user = request.user
        ApplicationRemark.objects.create(application=app_instance, message=message, author=logged_in_user)
        messages.success(request, "Message has been sent successfully!")

    return redirect(app_instance.get_partner_absolute_url)
