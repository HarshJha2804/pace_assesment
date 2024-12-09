from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.contrib.auth import get_user_model
from pace_project.core.enums import StatusTypeEnum
from pace_project.core.models.generic_models import GenericFollowUp
from pace_project.core.models.target_models import UniversityTarget, RMTarget
from pace_project.core.models.requirement_models import StaffingRequirement
from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import DocumentTemplate, PartnerSupportDocument, StatusType, \
    CountrySpecificStatus, CountrySpecificDocument, CountrySpecificLevel, CountrySpecificField, DynamicField, \
    CommissionStructure, UniversityInterviewStatus, InterviewStatusType, Condition, UpdateNews
from pace_project.meetcom.models import CommunicationType
from pace_project.paceapp.enums import RoleEnum
from pace_project.paceapp.models import Country, UniversityIntake, Intake
from pace_project.users.models import Employee, ContactUs
from ckeditor.widgets import CKEditorWidget

User = get_user_model()


class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('is_active', css_class='col-md-8'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class StatusTypeForm(forms.ModelForm):
    class Meta:
        model = StatusType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StatusTypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('priority', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class DynamicFieldTypeForm(forms.ModelForm):
    class Meta:
        model = DynamicField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DynamicFieldTypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PartnerSupportDocumentForm(forms.ModelForm):
    class Meta:
        model = PartnerSupportDocument
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PartnerSupportDocumentForm, self).__init__(*args, **kwargs)
        self.fields['university'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['intake'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['year'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['template'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['template'].label = 'Document Type'
        self.fields['template'].empty_label = 'Select Document Type'
        self.fields['university'].empty_label = 'Select University '
        self.fields['intake'].empty_label = 'Select Intake '
        self.fields['year'].empty_label = 'Select Year'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('university', css_class='col-md-6'),
                Div('intake', css_class='col-md-6'),
                Div('year', css_class='col-md-6'),
                Div('template', css_class='col-md-6'),
                Div('file', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class CountrySpecificStatusForm(forms.ModelForm):
    class Meta:
        model = CountrySpecificStatus
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CountrySpecificStatusForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_university=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['status_types'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['achievement_statuses'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['country'].empty_label = 'Select Country'
        self.fields['status_types'].empty_label = 'Select Status Types'
        self.fields['achievement_statuses'].empty_label = 'Select Achievement Statuses'
        self.fields['achievement_statuses'].label = ' Achievement Statuses'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('status_types', css_class='col-md-6'),
                Div('achievement_statuses', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class CountrySpecificDocumentForm(forms.ModelForm):
    class Meta:
        model = CountrySpecificDocument
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CountrySpecificDocumentForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_university=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['document_types'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['country'].empty_label = 'Select Country'
        self.fields['document_types'].empty_label = 'Select Document Types'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('document_types', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class StaffingRequirementForm(forms.ModelForm):
    class Meta:
        model = StaffingRequirement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StaffingRequirementForm, self).__init__(*args, **kwargs)
        self.fields['target_value'].label = 'Target'
        self.fields['rm_count'].label = 'Regional Marketing Head '
        self.fields['assessment_officer_count'].label = 'Assessment Officer'
        self.fields['application_manager_count'].label = 'Application Manager'
        self.fields['interviewer_count'].label = 'Interviewer'
        self.fields['visa_officer_count'].label = 'Visa Officer'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('target_value', css_class='col-md-4'),
                Div('rm_count', css_class='col-md-4'),
                Div('assessment_officer_count', css_class='col-md-4'),
                Div('application_manager_count', css_class='col-md-4'),
                Div('interviewer_count', css_class='col-md-4'),
                Div('visa_officer_count', css_class='col-md-4'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class UniversityTargetForm(forms.ModelForm):
    class Meta:
        model = UniversityTarget
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UniversityTargetForm, self).__init__(*args, **kwargs)
        self.fields['university'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['intake'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['year'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['university'].empty_label = 'Select University'
        self.fields['intake'].empty_label = 'Select intake'
        self.fields['year'].empty_label = 'Select Year'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('university', css_class='col-md-6'),
                Div('intake', css_class='col-md-6'),
                Div('year', css_class='col-md-6'),
                Div('target', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class ApplicationForm(forms.ModelForm):
    passport_number = forms.CharField(required=False, label='Passport Number')
    partner = forms.CharField(required=False, label='Partner')
    university = forms.CharField(required=False, label='University')
    student = forms.CharField(required=False, label='Student')
    course = forms.CharField(required=False, label='Course')

    class Meta:
        model = Application
        fields = ['current_status', 'intake', 'year']

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['intake'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['year'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['current_status'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['student'].widget.attrs['disabled'] = 'disabled'
        self.fields['course'].widget.attrs['disabled'] = 'disabled'
        self.fields['partner'].widget.attrs['disabled'] = 'disabled'
        self.fields['university'].widget.attrs['disabled'] = 'disabled'
        self.fields['intake'].empty_label = 'Select intake'
        self.fields['year'].empty_label = 'Select Year'
        self.fields['current_status'].empty_label = 'Select Status'
        # self.fields['application_manager'].empty_label = 'Select Application Manager'
        # self.fields['application_manager'].required = True
        # if employee and employee.assigned_country:
            # self.fields['application_manager'].queryset = User.objects.filter(
            #     is_active=True,
            #     role__name=RoleEnum.APPLICATION_MANAGER.value,
            #     employee__assigned_country=employee.assigned_country
            # ).order_by('name')
            # self.fields['application_manager'].label_from_instance = self.get_application_manager_label

        course = self.initial.get('course', None)

        if course:
            # course_university = course.university
            # self.fields['application_manager'].queryset = self.fields['application_manager'].queryset.filter(
            #     employee__assigned_universities__in=[course_university]
            # )

            try:
                # Filter to show only "Application Pending From IOA" status
                status_type = StatusType.objects.get(
                    name=StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value
                )
                self.fields['current_status'].queryset = CountrySpecificStatus.objects.filter(
                    country=course.university.country,
                    status_types=status_type
                ).first().status_types.filter(id=status_type.id)
            except StatusType.DoesNotExist:
                self.fields['current_status'].queryset = StatusType.objects.none()

        # Set the initial value for passport_number if available
        passport_number = self.initial.get('passport_number', None)
        if passport_number:
            self.fields['passport_number'].initial = passport_number

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('student', css_class='col-md-6'),
                Div('partner', css_class='col-md-6'),
                Div('university', css_class='col-md-6'),
                Div('passport_number', css_class='col-md-6'),
                Div('course', css_class='col-md-6'),
                Div('intake', css_class='col-md-6'),
                Div('year', css_class='col-md-6'),
                Div('current_status', css_class='col-md-6'),
                # Div('application_manager', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        if passport_number in [None, '', '0']:
            raise forms.ValidationError('Passport number cannot be 0 or blank')
        return passport_number

    def get_application_manager_label(self, obj):
        return f"{obj.name}"


class ApplicationStatusForm(forms.ModelForm):
    passport_number = forms.CharField(required=False, label='Passport Number', disabled=True)
    partner = forms.CharField(required=False, label='Partner')
    remark = forms.CharField(required=True, label='Remark')

    intake = forms.ModelChoiceField(
        queryset=UniversityIntake.objects.all(),
        required=True,
        label="Intake"
    )

    class Meta:
        model = Application
        fields = ['current_status', 'student', 'medical_status', 'intake', 'year', 'funds_status', 'interview_status',
                  'conditions',
                  'offer_id', 'offer_status']

    def __init__(self, *args, **kwargs):
        super(ApplicationStatusForm, self).__init__(*args, **kwargs)
        self.dynamic_fields = None
        if self.instance:
            student = self.instance.student
            if student.study_country:
                # Fetch and configure dynamic fields based on the student's study country
                self._configure_dynamic_fields(student.study_country)

        self.fields['student'].disabled = True
        self.fields['partner'].widget.attrs['disabled'] = 'disabled'
        self.fields['conditions'].widget = forms.CheckboxSelectMultiple()
        self.fields['conditions'].queryset = Condition.objects.filter(is_active=True)
        self.fields['conditions'].widget.attrs.update({'data-searchable': 'true'})

        # Dynamically populate intake field with individual intakes
        if self.instance and self.instance.course and self.instance.course.university:
            university = self.instance.course.university
            university_intakes = UniversityIntake.objects.filter(
                university=university, is_active=True
            )
            self.fields['intake'].queryset = Intake.objects.filter(
                universityintake__in=university_intakes
            ).distinct()
            self.fields['intake'].label_from_instance = lambda obj: obj.intake_month

        if self.instance:
            course = self.instance.course
            self.fields['current_status'].queryset = CountrySpecificStatus.objects.filter(
                country=course.university.country
            ).first().status_types.all()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('student', css_class='col-md-2 me-3'),
                Div('partner', css_class='col-md-2 me-3'),
                Div('passport_number', css_class='col-md-2 me-3'),
                Div('intake', css_class='col-md-2 me-3'),
                Div('year', css_class='col-md-2 me-3'),
                Div('current_status', css_class='col-md-3 me-3'),
                Div('offer_id', css_class='col-md-3 me-3'),
                Div('offer_status', css_class='col-md-3 me-3'),
                Div('conditions', css_class='col-md-3 me-3'),
                Div('medical_status', css_class='col-md-3 me-3'),
                Div('funds_status', css_class='col-md-3 me-3'),
                Div('interview_status', css_class='col-md-3 me-3'),
                Div('remark', css_class='col-md-3 me-3'),
                *self._dynamic_field_layout(),
                css_class='d-flex justify-content-between overflow-auto',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def _dynamic_field_layout(self):
        layout = []
        if self.dynamic_fields:
            for field in self.dynamic_fields:
                layout.append(Div(field.slugified_name, css_class='col-md-2 me-2'))
        return layout

    def _configure_dynamic_fields(self, country):
        """
        Fetch and add dynamic fields based on the given country.
        """
        country_field_obj = CountrySpecificField.objects.filter(
            country=country
        ).first()

        if country_field_obj:
            dynamic_fields = country_field_obj.fields.filter(is_active=True)
            self.dynamic_fields = dynamic_fields
            for field in dynamic_fields:
                self.fields[field.slugified_name] = forms.CharField(
                    required=False,
                    label=field.name
                )


class RMTargetForm(forms.ModelForm):
    class Meta:
        model = RMTarget
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RMTargetForm, self).__init__(*args, **kwargs)
        self.fields['rm'].queryset = Employee.objects.filter(
            user__role__name=RoleEnum.REGIONAL_MARKETING_HEAD.value)
        self.fields['rm'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['university'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['partner'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['intake'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['year'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['rm'].label = 'Regional Marketing Head'
        self.fields['rm'].empty_label = 'Select Regional Marketing Head'
        self.fields['university'].empty_label = 'Select University'
        self.fields['partner'].empty_label = 'Select Partner'
        self.fields['intake'].empty_label = 'Select Intake'
        self.fields['year'].empty_label = 'Select Year'
        self.fields['target'].empty_label = 'Add Target'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('rm', css_class='col-md-4'),
                Div('university', css_class='col-md-4'),
                Div('partner', css_class='col-md-4'),
                Div('intake', css_class='col-md-4'),
                Div('year', css_class='col-md-4'),
                Div('target', css_class='col-md-4'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class FollowUpForm(forms.ModelForm):
    contact_method = forms.ModelChoiceField(
        queryset=CommunicationType.objects.filter(is_active=True), empty_label="Select contact method",
    )

    class Meta:
        model = GenericFollowUp
        fields = [
            'content_type',
            'object_id',
            'follow_up_date',
            'follow_up_time',
            'follow_up_note',
            'contact_method',
        ]

    def __init__(self, *args, **kwargs):
        super(FollowUpForm, self).__init__(*args, **kwargs)
        self.fields['follow_up_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['follow_up_time'].widget = forms.DateInput(attrs={'type': 'time'})

        self.fields['content_type'].widget = forms.HiddenInput()
        self.fields['object_id'].widget = forms.HiddenInput()
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Div(

                Div('follow_up_date', css_class='col-md-6'),
                Div('follow_up_time', css_class='col-md-6'),
                Div('contact_method', css_class='col-md-12'),
                Div('follow_up_note', css_class='col-md-12'),
                Div('content_type', css_class='col-md-6'),
                Div('object_id', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class CountrySpecificLevelForm(forms.ModelForm):
    class Meta:
        model = CountrySpecificLevel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CountrySpecificLevelForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_university=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['levels'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['country'].empty_label = 'Select Country'
        self.fields['levels'].empty_label = 'Select Level'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('levels', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class CountrySpecificFieldForm(forms.ModelForm):
    class Meta:
        model = CountrySpecificField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CountrySpecificFieldForm, self).__init__(*args, **kwargs)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select Country'
        self.fields['fields'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['fields'].empty_label = 'Select fields'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('fields', css_class='col-md-6'),
                Div('is_active', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False


class CommissionStructureForm(forms.ModelForm):
    class Meta:
        model = CommissionStructure
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CommissionStructureForm, self).__init__(*args, **kwargs)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select Country'

        self.fields['university'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['university'].empty_label = 'Select university'

        self.fields['year'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['year'].empty_label = 'Select year'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('university', css_class='col-md-6'),
                Div('year', css_class='col-md-6'),
                Div('commission', css_class='col-md-6'),
                Div('is_active', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False


class InterviewStatusTypeForm(forms.ModelForm):
    class Meta:
        model = InterviewStatusType
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(InterviewStatusTypeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(

                Div('name', css_class='col-md-6'),
                Div('is_mock', css_class='col-md-6'),
                Div('priority', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False


class UniversityInterviewStatusForm(forms.ModelForm):
    class Meta:
        model = UniversityInterviewStatus
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UniversityInterviewStatusForm, self).__init__(*args, **kwargs)

        self.fields['university'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['university'].empty_label = 'Select university'

        self.fields['status_types'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['status_types'].empty_label = 'Select status types'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(

                Div('university', css_class='col-md-6'),
                Div('status_types', css_class='col-md-6'),
                Div('is_active', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False


class ConditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('is_active', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = Condition
        fields = '__all__'


class UpdateNewsForm(forms.ModelForm):
    update = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = UpdateNews
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UpdateNewsForm, self).__init__(*args, **kwargs)
        self.fields['country'].help_text = None
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select country'
        self.fields['is_active'].widget = forms.HiddenInput()
        self.fields['created_by'].widget = forms.HiddenInput()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(

                Div('country', css_class='col-md-6'),
                Div('image', css_class='col-md-6'),
                Div('created_by', css_class='col-md-6'),
                Div('is_active', css_class='col-md-4'),
                Div('update', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = "__all__"
        exclude = ['content_type', 'object_id', 'content_object']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContactUsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['send_by'].widget = forms.HiddenInput()
        self.fields['is_active'].widget = forms.HiddenInput()
        self.fields['status'].widget = forms.HiddenInput()
        self.fields['description'].required = True

        if user and hasattr(user, 'partner') and user.partner.state:
            partner_region = user.partner.state.region
            if partner_region:
                self.fields['connect_to'].queryset = User.objects.filter(
                    employee__assigned_regions=partner_region,
                    role__name=RoleEnum.PARTNER_ACCOUNT_MANAGER.value
                )
                # Set default selection to the first account manager
                account_manager = self.fields['connect_to'].queryset.first()
                if account_manager:
                    self.initial['connect_to'] = account_manager  # Set default value
            else:
                self.fields['connect_to'].queryset = User.objects.none()
        else:
            self.fields['connect_to'].queryset = User.objects.none()

        self.helper.layout = Layout(
            Div(

                Div('subject', css_class='col-md-6'),
                Div('connect_to', css_class='col-md-6'),
                Div('status', css_class='col-md-6'),
                Div('send_by', css_class='col-md-6'),
                Div('content_type', css_class='col-md-6'),
                Div('object_id', css_class='col-md-6'),
                Div('content_object', css_class='col-md-6'),
                Div('description', css_class='col-md-12'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False


class ReplyForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = "__all__"
        exclude = ['content_type', 'object_id', 'content_object']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['send_by'].widget = forms.HiddenInput()
        self.fields['is_active'].widget = forms.HiddenInput()
        self.fields['status'].widget = forms.HiddenInput()
        self.fields['description'].required = True
        self.fields['status'].initial = 'replied'

        if 'send_by' in self.initial:
            self.fields['connect_to'].disabled = True

        self.fields['status'].default = 'Replied'

        self.helper.layout = Layout(
            Div(

                Div('subject', css_class='col-md-6'),
                Div('connect_to', css_class='col-md-6'),
                Div('status', css_class='col-md-6'),
                Div('send_by', css_class='col-md-6'),
                Div('content_type', css_class='col-md-6'),
                Div('object_id', css_class='col-md-6'),
                Div('content_object', css_class='col-md-6'),
                Div('description', css_class='col-md-12'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = False
