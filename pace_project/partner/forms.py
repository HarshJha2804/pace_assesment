from allauth.account.adapter import get_adapter
from allauth.account.forms import SignupForm
from allauth.account.utils import setup_user_email
from allauth.account.models import EmailAddress
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from pace_project.core.enums import StatusTypeEnum
from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import CountrySpecificLevel, StatusType, CountrySpecificStatus
from pace_project.core.models.generic_models import GenericDocument, GenericRemark
from pace_project.paceapp.enums import RoleEnum, LevelEnum
from pace_project.paceapp.models import Country, State, Level, Year, Course, Intake, University
from pace_project.partner.models import PartnerCommission, PartnerCommissionSetup
from pace_project.users.middlewares import get_current_request
from pace_project.users.models import Role, Partner, Student, Employee, PartnerAgreement, UGStudentAcademic, \
    PGStudentAcademic
from pace_project.utils.validators import validate_unique_company_email, validate_unique_legal_name, \
    validate_company_unique_trade_name
from django.contrib.auth import get_user_model

User = get_user_model()


class PartnerSignupForm(SignupForm):
    COMPANY_TYPE_CHOICES = [
        ('', 'Select a company type'),
        ('Proprietorship', 'Proprietorship'),
        ('Partnership', 'Partnership'),
        ('Pvt. Limited', 'Pvt. Limited'),
        ('Public', 'Public'),
        ('LLP', 'LLP'),
        ('Limited', 'Limited'),
        ('Other', 'Other'),
    ]

    company_name = forms.CharField(
        label=_("Company Name"), widget=forms.TextInput(attrs={'placeholder': 'Company Name'}),
        validators=[validate_company_unique_trade_name],
    )
    company_legal_name = forms.CharField(
        label=_("Registered Company Name (Optional)"), required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Registered Company Name'}),
        validators=[validate_unique_legal_name]
    )
    company_type = forms.ChoiceField(
        choices=COMPANY_TYPE_CHOICES, widget=forms.Select(attrs={'data-searchable': 'true'})
    )

    email = forms.EmailField(
        label=_("Email"), widget=forms.EmailInput(attrs={'placeholder': 'Company Email'}),
        validators=[validate_unique_company_email]
    )
    country_code = forms.ModelChoiceField(
        queryset=Country.objects.all(), widget=forms.Select(attrs={'data-searchable': 'true'}),
        empty_label='Select a country'
    )
    mobile_number = forms.CharField(
        label=_("Mobile Number"), widget=forms.NumberInput(attrs={'placeholder': 'Mobile Number'})
    )
    whatsapp_country_code = forms.ModelChoiceField(
        queryset=Country.objects.all(), widget=forms.Select(attrs={'data-searchable': 'true'}), label="Country Code",
        empty_label="Select Country", required=False
    )
    whatsapp_number = forms.CharField(
        label=_("WhatsApp Number"), widget=forms.NumberInput(attrs={'placeholder': 'WhatsApp Number'}), required=False
    )

    address = forms.CharField(
        label=_("Company Registered Address"),
        widget=forms.TextInput(attrs={'placeholder': 'Company Registered Address'})
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), widget=forms.Select(attrs={'data-searchable': 'true'}),
        empty_label='Select Country'
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.all(), required=False,
        empty_label='Select State'
    )
    city = forms.CharField(label=_("City"), widget=forms.TextInput(attrs={'placeholder': 'City'}))
    pincode = forms.CharField(
        label=_("Pincode"), required=False, widget=forms.NumberInput(attrs={'placeholder': 'Pincode'})
    )

    first_name = forms.CharField(
        label=_("First Name"), widget=forms.TextInput(attrs={'placeholder': 'Contact Person First Name'})
    )
    last_name = forms.CharField(
        label=_("Last Name"), required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Contact Person Last Name'})
    )
    designation = forms.CharField(
        label=_("Designation"), widget=forms.TextInput(attrs={'placeholder': 'Designation'}), required=False
    )
    website = forms.CharField(
        label=_("Website"), required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Website Link'})
    )
    logo = forms.ImageField(label=_("Logo"), required=False)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, required=True, label="reCAPTCHA")

    def __init__(self, *args, **kwargs):
        super(PartnerSignupForm, self).__init__(*args, **kwargs)
        self.fields['country_code'].label_from_instance = lambda obj: obj.country_code if obj.country_code else '-'
        self.fields['whatsapp_country_code'].label_from_instance = lambda \
                obj: obj.country_code if obj.country_code else '-'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('company_name', css_class='col-md-4'),
                Div('company_legal_name', css_class='col-md-4'),
                Div('company_type', css_class='col-md-4'),
                Div('first_name', css_class='col-md-4'),
                Div('last_name', css_class='col-md-4'),
                Div('designation', css_class='col-md-4'),
                Div('email', css_class='col-md-4'),
                Div('country_code', css_class='col-md-4'),
                Div('mobile_number', css_class='col-md-4'),
                Div('whatsapp_country_code', css_class='col-md-4'),
                Div('whatsapp_number', css_class='col-md-4'),
                Div('address', css_class='col-md-4'),
                Div('country', css_class='col-md-4'),
                Div('state', css_class='col-md-4'),
                Div('city', css_class='col-md-2'),
                Div('pincode', css_class='col-md-2'),
                Div('website', css_class='col-md-4'),
                Div('logo', css_class='col-md-4'),
                Div('password1', css_class='col-md-4'),
                Div('password2', css_class='col-md-4'),
                Div('captcha', css_class='col-md-4'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean(self):
        cleaned_data = super().clean()

        captcha_response = cleaned_data.get('captcha')
        if not captcha_response:
            request = get_current_request()
            from django.contrib import messages
            messages.error(request, "reCAPTCHA validation failed. Please try again.")
            self.add_error('captcha', 'reCAPTCHA validation failed. Please try again.')
        return cleaned_data

    def create_partner(self, user: User):
        if user:
            legal_name = self.cleaned_data.get("company_legal_name")
            company_type = self.cleaned_data.get("company_type")

            country_code = self.cleaned_data.get("country_code")
            mobile_number = self.cleaned_data.get("mobile_number")
            whatsapp_country_code = self.cleaned_data.get("whatsapp_country_code")
            whatsapp_number = self.cleaned_data.get("whatsapp_number")

            address = self.cleaned_data.get("address")
            country = self.cleaned_data.get("country")
            state = self.cleaned_data.get("state")
            city = self.cleaned_data.get("city")
            pincode = self.cleaned_data.get("pincode")
            first_name = self.cleaned_data.get("first_name")
            last_name = self.cleaned_data.get("last_name")
            designation = self.cleaned_data.get("designation")
            website = self.cleaned_data.get("website")
            logo = self.cleaned_data.get("logo")

            instance = Partner(
                user=user, company_name=user.name, email=user.email, country=country, company_type=company_type,
                mobile_country_code=country_code, mobile_number=mobile_number
            )
            if legal_name:
                instance.legal_name = legal_name

            instance.whatsapp_country_code = whatsapp_country_code
            instance.whatsapp_number = whatsapp_number

            instance.address = address
            if state:
                instance.state = state

            instance.city = city
            if pincode:
                instance.pincode = pincode

            if last_name:
                instance.contact_name = f"{first_name} {last_name}"
            else:
                instance.contact_name = first_name

            if website:
                instance.website = website

            if logo:
                instance.logo = logo

            if designation:
                instance.designation = designation

            instance.on_boarded_by = user
            instance.save()

    def custom_signup(self, request, user):
        super().custom_signup(request, user)
        try:
            partner_role_object = Role.objects.get(name=RoleEnum.PARTNER.value)
            user.role = partner_role_object
            company_name = self.cleaned_data.get("company_name")
            logo = self.cleaned_data.get("logo")
            user.name = company_name
            if logo:
                user.avatar = logo
            user.save()
            self.create_partner(user)

        except Role.DoesNotExist as e:
            print("custom signup exception call ")

    def save(self, request):
        email = self.cleaned_data.get("email")
        if self.account_already_exists:
            raise ValueError(email)
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self, commit=False)
        self.custom_signup(request, user)
        # TODO: Move into adapter `save_user` ?
        setup_user_email(request, user, [EmailAddress(email=email)] if email else [])
        return user


class StudentCreateForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }), required=False)
    country_on_passport = forms.ModelChoiceField(queryset=Country.objects.all())

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['is_active', 'created_by', 'assessment_status', 'partner']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['study_country'].empty_label = 'Select Destination'
        self.fields['study_country'].queryset = Country.objects.filter(is_active_for_university=True)
        self.fields['country_on_passport'].queryset = Country.objects.all()

        self.fields['study_country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country_on_passport'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['study_level'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['study_country'].required = True

        self.fields['study_level'].empty_label = 'Select Study Level'
        self.fields['country_on_passport'].empty_label = 'Select Country On Passport'
        self.fields['study_level'].required = True
        self.fields['date_of_birth'].required = True

        self.fields['type'].required = False
        self.fields['passport_number'].required = True
        self.fields['type'].label = "Student Type"
        self.fields['study_country'].label = "Destination"

        if self.instance and self.instance.pk:
            study_level = self.instance.study_level
            if study_level:
                if study_level.level == LevelEnum.UNDERGRADUATE.value:
                    ug_academic = UGStudentAcademic.objects.filter(student=self.instance).first()
                    if ug_academic:
                        self.fields['country_on_passport'].initial = ug_academic.country

                elif study_level.level == LevelEnum.POSTGRADUATE.value:
                    pg_academic = PGStudentAcademic.objects.filter(student=self.instance).first()
                    if pg_academic:
                        self.fields['country_on_passport'].initial = pg_academic.country

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(

                Div('first_name', css_class='col-md-3'),
                Div('middle_name', css_class='col-md-3'),
                Div('last_name', css_class='col-md-3'),
                Div('passport_number', css_class='col-md-3'),
                Div('date_of_birth', css_class='col-md-3'),
                Div('email', css_class='col-md-3'),
                Div('mobile_number', css_class='col-md-3'),
                Div('country_on_passport', css_class='col-md-3'),
                Div('type', css_class='col-md-3'),
                Div('study_country', css_class='col-md-3'),
                Div('study_level', css_class='col-md-3'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        if passport_number == '0' or not passport_number:
            raise forms.ValidationError("Passport number cannot be '0' or blank.")
        return passport_number


class PartnerAgreementForm(forms.ModelForm):
    class Meta:
        model = PartnerAgreement
        fields = '__all__'
        exclude = ['partner']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('year'):
            self.fields['year'].initial = datetime.now().year
        self.fields['year'].widget = forms.HiddenInput()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('agreement', css_class='col-md-12'),
                Div('year', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PassportForm(forms.Form):
    passport_number = forms.CharField(max_length=50, label="Enter Passport Number")


class PartnerGenericDocumentForm(forms.ModelForm):
    class Meta:
        model = GenericDocument
        fields = ['document_type', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_type'].empty_label = "Select Document Type"
        initial_document_types = self.initial.get('document_type')
        if initial_document_types:
            self.fields['document_type'].queryset = initial_document_types
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('document_type', css_class='col-md-12'),
                Div('file', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PartnerApplicationForm(forms.ModelForm):
    passport_number = forms.CharField(required=False, label='Passport Number')
    university = forms.CharField(required=False, label='University')
    student = forms.CharField(required=False, label='Student')

    class Meta:
        model = Application
        fields = ['current_status', 'intake', 'year', 'university', "course"]

    def __init__(self, *args, **kwargs):
        super(PartnerApplicationForm, self).__init__(*args, **kwargs)

        self.fields['student'].widget.attrs['disabled'] = 'disabled'
        self.fields['university'].widget.attrs['disabled'] = 'disabled'
        initial_course = self.initial.get("course", None)
        if initial_course:
            courses = Course.objects.filter(
                name__iexact=initial_course.name, university=initial_course.university,
                is_active=True
            )
            self.fields['course'].queryset = courses

        # Set default current status to "Application Pending From IOA"
        try:
            status_type = StatusType.objects.get(name=StatusTypeEnum.APPLICATION_PENDING_FROM_IOA.value)
            self.fields['current_status'].initial = status_type  # Set default status
            self.fields['current_status'].queryset = StatusType.objects.filter(id=status_type.id)
            self.fields['current_status'].widget = forms.HiddenInput()
        except StatusType.DoesNotExist:
            self.fields['current_status'].queryset = StatusType.objects.none()

        self.fields['year'].queryset = Year.objects.current_to_future()
        # Set initial passport number if available
        passport_number = self.initial.get('passport_number', None)
        if passport_number:
            self.fields['passport_number'].initial = passport_number

        intakes = self.initial.get("intake", None)
        if intakes:
            self.fields['intake'].queryset = intakes

        # Form layout customization without 'application_manager'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('student', css_class='col-md-6'),
                Div('university', css_class='col-md-6'),
                Div('passport_number', css_class='col-md-6'),
                Div('course', css_class='col-md-6'),
                Div('intake', css_class='col-md-6'),
                Div('year', css_class='col-md-6'),
                Div('current_status', css_class='col-md-6'),
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


class ApplyApplicationForm(forms.ModelForm):
    passport_number = forms.CharField(required=False, label='Passport Number')
    partner = forms.CharField(required=False, label='Partner')
    university = forms.CharField(required=False, label='University')
    student = forms.CharField(required=False, label='Student')
    course = forms.CharField(required=False, label='Course')

    class Meta:
        model = Application
        fields = ['current_status', 'intake', 'year']  # Removed 'application_manager'

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super(ApplyApplicationForm, self).__init__(*args, **kwargs)
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

        self.fields['current_status'].widget = forms.HiddenInput()

        course = self.initial.get('course', None)

        if course:
            course_university = course.university

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


class PartnerCommissionForm(forms.ModelForm):
    remark = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = PartnerCommission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PartnerCommissionForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})

        if 'university' in self.initial:
            if not user.is_superuser:
                self.fields['university'].disabled = True

        if 'partner' in self.initial:
            self.fields['partner'].disabled = True

        self.fields['university'].empty_label = "Select University"
        self.fields['created_by'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('university', css_class='col-md-6'),
                Div('partner', css_class='col-md-6'),
                Div('date', css_class='col-md-6'),
                Div('commission_type', css_class='col-md-6'),
                Div('commission', css_class='col-md-6'),
                Div('created_by', css_class='col-md-6'),
                Div('remark', css_class='col-md-12'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )

        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean_commission(self):
        commission = self.cleaned_data.get('commission')
        if commission is None or commission <= 0:
            raise ValidationError("Commission must be greater than zero.")
        return commission

    def create_remark(self, user: User, partner_id: int):
        remark = self.cleaned_data.get('remark')
        if remark:
            instance = GenericRemark(
                content_object=Partner.objects.get(id=partner_id),
                created_by=user,
                remark=remark,
            )

            instance.save()


class SetPartnerCommissionForm(forms.ModelForm):
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)

    class Meta:
        model = PartnerCommissionSetup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(SetPartnerCommissionForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_student=True)
        self.fields['intake'].widget.attrs.update({'id': 'id_intake'})

        self.fields['intake'].queryset = Intake.objects.none()
        if 'university' in self.data:
            try:
                university_id = int(self.data.get('university'))
                self.fields['intake'].queryset = Intake.objects.filter(
                    universityintake__university_id=university_id,
                    universityintake__is_active=True
                ).distinct()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['intake'].queryset = self.instance.university.universityintake_set.filter(
                is_active=True
            ).values_list('intakes', flat=True)

        self.fields['university'].empty_label = "Select University"
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['year'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['intake'].empty_label = "Select Intake"
        self.fields['year'].empty_label = "Select Year"
        self.fields['country'].empty_label = "Select Country"
        self.fields['commission_type'].empty_label = "Select Commission Type"
        self.fields['commission_type'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['bonus_type'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['commission_frequency'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['slabs'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['commission_on'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['slabs'].empty_label = "Select Slab"
        self.fields['bonus_type'].empty_label = "Select Bonus Type"
        self.fields['commission_on'].choices = [("", "Select Commission On")] + list(
            self.fields['commission_on'].choices)
        self.fields['commission_frequency'].choices = [("", "Select Commission Frequency")] + list(
            University.MEDIUM_CHOICES)
        self.fields['created_by'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('university', css_class='col-md-4'),
                Div('intake', css_class='col-md-4'),
                Div('year', css_class='col-md-4'),
                Div('country', css_class='col-md-4'),
                Div('region', css_class='col-md-4'),
                Div('commission_type', css_class='col-md-4'),
                Div('commission', css_class='col-md-4'),
                Div('slabs', css_class='col-md-4'),
                Div('bonus_type', css_class='col-md-4'),
                Div('commission_on', css_class='col-md-4'),
                Div('tution_fee_for_commission', css_class='col-md-4'),
                Div('commission_frequency', css_class='col-md-4'),
                Div('comments', css_class='col-md-12'),
                Div('created_by', css_class='col-md-4'),
                css_class='row',
            ),
        )

        self.helper.form_tag = False
        self.helper.disable_csrf = True
