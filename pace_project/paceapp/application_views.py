from django.contrib import messages
from django.db import transaction
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from pace_project.core.emails import send_application_status_update_email, send_partner_application_message_email
from pace_project.core.enums import StatusTypeEnum
from pace_project.core.forms import ApplicationForm, ApplicationStatusForm
from pace_project.core.notifications import notify_partner_on_status_change
from pace_project.paceapp.actstream import generate_new_application_stream, generate_updated_application_stream
from pace_project.paceapp.models import AssessmentDiscovery
from pace_project.core.models.application_models import Application, ApplicationRemark, ApplicationAttribute, \
    ApplicationStatusLog
from pace_project.core.models.core_models import StatusType, CountrySpecificField
from pace_project.paceapp.services import notify_partner_on_message_sent


class ApplyApplicationView(DetailView, FormMixin):
    model = AssessmentDiscovery
    form_class = ApplicationForm
    template_name = "core/application/apply_form.html"

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
            form.save_m2m()

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
            messages.success(request, 'Application has been successfully applied.')
            return redirect('paceapp:student_detail', pk=self.object.student.pk)

        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self.request.user, 'employee'):
            kwargs['employee'] = self.request.user.employee
        return kwargs


class UpdateApplicationStatusView(UpdateView):
    model = Application
    form_class = ApplicationStatusForm
    template_name = "core/application/update_application_status_form.html"

    def get_object(self, queryset=None):
        """
        Override the get_object method to fetch the Application instance
        with related fields in a single query using select_related().
        """
        return Application.objects.select_related('student', 'student__partner').get(pk=self.kwargs['pk'])

    def get_initial(self):
        self.pre_status = self.object.current_status.name
        initial = super().get_initial()
        student = self.object.student
        initial.update({
            'partner': student.partner,
            'passport_number': student.passport_number
        })

        student = self.object.student
        self.dynamic_fields = None

        # Configure dynamic fields and their values
        if student.study_country:
            self._populate_dynamic_fields(student.study_country, initial)

        return initial

    def _populate_dynamic_fields(self, country, initial):
        """
        Populate initial data for dynamic fields based on the given country.
        """
        country_fields = CountrySpecificField.objects.filter(
            country=country
        ).select_related('country').first()

        if country_fields:
            dynamic_fields = country_fields.fields.filter(is_active=True)
            self.dynamic_fields = dynamic_fields
            dynamic_attrs = ApplicationAttribute.objects.filter(
                application=self.object,
                field__in=dynamic_fields
            ).select_related('field')

            for attr in dynamic_attrs:
                initial[attr.field.slugified_name] = attr.value

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            # Handle remark creation
            self._create_application_remark(form.cleaned_data.get('remark'))

            # Handle dynamic fields
            self._handle_dynamic_fields(form)
            notify_partner_on_status_change(application=self.object, sender=self.request.user)
            send_application_status_update_email(application=self.object, remark=form.cleaned_data.get("remark"))
            generate_updated_application_stream(
                current_user=self.request.user, previous_status=self.pre_status, application=self.object
            )
            return response

    def _create_application_remark(self, remark_content):
        """
        Create an application remark if the remark_content is present.
        """
        if remark_content:
            ApplicationRemark.objects.create(
                application=self.object,
                message=remark_content,
                author=self.request.user,
                is_active=True
            )

    def _handle_dynamic_fields(self, form):
        """
        Update or create dynamic fields in the ApplicationAttribute model.
        """
        if self.dynamic_fields:
            for field in self.dynamic_fields:
                field_value = form.cleaned_data.get(field.slugified_name)
                if field_value:
                    instance, created = ApplicationAttribute.objects.update_or_create(
                        application=self.object,
                        field=field,
                        defaults={'value': field_value}
                    )
                    if created:
                        instance.created_by = self.request.user
                        instance.save()

    def get_success_url(self):
        messages.success(self.request, 'Application Status has been successfully updated!')
        return reverse("core:application_list")


class UpdateComplianceApplicationStatusView(UpdateView):
    model = Application
    form_class = ApplicationStatusForm
    template_name = "core/application/update_compliance_application_status_form.html"

    def get_object(self, queryset=None):
        """
        Override the get_object method to fetch the Application instance
        with related fields in a single query using select_related().
        """
        return Application.objects.select_related('student', 'student__partner').get(pk=self.kwargs['pk'])

    def get_initial(self):
        self.pre_status = self.object.current_status.name
        initial = super().get_initial()
        student = self.object.student
        initial.update({
            'partner': student.partner,
            'passport_number': student.passport_number
        })

        student = self.object.student
        self.dynamic_fields = None

        # Configure dynamic fields and their values
        if student.study_country:
            self._populate_dynamic_fields(student.study_country, initial)

        return initial

    def _populate_dynamic_fields(self, country, initial):
        """
        Populate initial data for dynamic fields based on the given country.
        """
        country_fields = CountrySpecificField.objects.filter(
            country=country
        ).select_related('country').first()

        if country_fields:
            dynamic_fields = country_fields.fields.filter(is_active=True)
            self.dynamic_fields = dynamic_fields
            dynamic_attrs = ApplicationAttribute.objects.filter(
                application=self.object,
                field__in=dynamic_fields
            ).select_related('field')

            for attr in dynamic_attrs:
                initial[attr.field.slugified_name] = attr.value

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        excluded_statuses = [
            'Assessment Sent',
            'Assessment Rejected',
            'Pending From IG',
            'Pending From Partner'
        ]
        form.fields['current_status'].queryset = form.fields['current_status'].queryset.exclude(
            name__in=excluded_statuses)
        return form

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            # Handle remark creation
            self._create_application_remark(form.cleaned_data.get('remark'))

            # Handle dynamic fields
            self._handle_dynamic_fields(form)

            generate_updated_application_stream(
                current_user=self.request.user, previous_status=self.pre_status, application=self.object
            )
            return response

    def _create_application_remark(self, remark_content):
        """
        Create an application remark if the remark_content is present.
        """
        if remark_content:
            ApplicationRemark.objects.create(
                application=self.object,
                message=remark_content,
                author=self.request.user,
                is_active=True
            )

    def _handle_dynamic_fields(self, form):
        """
        Update or create dynamic fields in the ApplicationAttribute model.
        """
        if self.dynamic_fields:
            for field in self.dynamic_fields:
                field_value = form.cleaned_data.get(field.slugified_name)
                if field_value:
                    instance, created = ApplicationAttribute.objects.update_or_create(
                        application=self.object,
                        field=field,
                        defaults={'value': field_value}
                    )
                    if created:
                        instance.created_by = self.request.user
                        instance.save()

    def get_success_url(self):
        messages.success(self.request, 'Application Status has been successfully updated!')
        return reverse("paceapp:compliance_application_list")


class UpdateApplicationManagerApplicationStatusView(UpdateView):
    model = Application
    form_class = ApplicationStatusForm
    template_name = "core/application/update_application_manager_application_status_form.html"

    def get_object(self, queryset=None):
        """
        Override the get_object method to fetch the Application instance
        with related fields in a single query using select_related().
        """
        return Application.objects.select_related('student', 'student__partner').get(pk=self.kwargs['pk'])

    def get_initial(self):
        self.pre_status = self.object.current_status.name
        initial = super().get_initial()
        student = self.object.student
        initial.update({
            'partner': student.partner,
            'passport_number': student.passport_number
        })

        student = self.object.student
        self.dynamic_fields = None

        # Configure dynamic fields and their values
        if student.study_country:
            self._populate_dynamic_fields(student.study_country, initial)

        return initial

    def _populate_dynamic_fields(self, country, initial):
        """
        Populate initial data for dynamic fields based on the given country.
        """
        country_fields = CountrySpecificField.objects.filter(
            country=country
        ).select_related('country').first()

        if country_fields:
            dynamic_fields = country_fields.fields.filter(is_active=True)
            self.dynamic_fields = dynamic_fields
            dynamic_attrs = ApplicationAttribute.objects.filter(
                application=self.object,
                field__in=dynamic_fields
            ).select_related('field')

            for attr in dynamic_attrs:
                initial[attr.field.slugified_name] = attr.value

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Define the allowed statuses
        allowed_statuses = [
            'Pending From IG',
            'Pending From Partner',
            'Application Submitted',
            'Prescreening Pending'
        ]

        # Filter the current_status queryset to show only the allowed statuses
        form.fields['current_status'].queryset = form.fields['current_status'].queryset.filter(
            name__in=allowed_statuses
        )

        return form

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            # Handle remark creation
            self._create_application_remark(form.cleaned_data.get('remark'))

            # Handle dynamic fields
            self._handle_dynamic_fields(form)

            generate_updated_application_stream(
                current_user=self.request.user, previous_status=self.pre_status, application=self.object
            )
            return response

    def _create_application_remark(self, remark_content):
        """
        Create an application remark if the remark_content is present.
        """
        if remark_content:
            ApplicationRemark.objects.create(
                application=self.object,
                message=remark_content,
                author=self.request.user,
                is_active=True
            )

    def _handle_dynamic_fields(self, form):
        """
        Update or create dynamic fields in the ApplicationAttribute model.
        """
        if self.dynamic_fields:
            for field in self.dynamic_fields:
                field_value = form.cleaned_data.get(field.slugified_name)
                if field_value:
                    instance, created = ApplicationAttribute.objects.update_or_create(
                        application=self.object,
                        field=field,
                        defaults={'value': field_value}
                    )
                    if created:
                        instance.created_by = self.request.user
                        instance.save()

    def get_success_url(self):
        messages.success(self.request, 'Application Status has been successfully updated!')
        return reverse("paceapp:application_manager_application_list")


def chat_with_partner_view(request, pk):
    app_instance = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        message = request.POST.get("message")
        logged_in_user = request.user
        appr_obj = ApplicationRemark.objects.create(application=app_instance, message=message, author=logged_in_user)
        if appr_obj:
            notify_partner_on_message_sent(app_remark=appr_obj)
            send_partner_application_message_email(app_remark=appr_obj)
            messages.success(request, "Message has been sent successfully!")

    return redirect(app_instance.get_absolute_url)
