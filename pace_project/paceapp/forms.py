from allauth.account.adapter import get_adapter
from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.forms.utils import ErrorList

from pace_project.core.models.core_models import CountrySpecificLevel, PartnerOnBoardingRequest, DailyProgressReport
from pace_project.core.models.generic_models import GenericDocument
from pace_project.paceapp.enums import UGAcademicPathWayEnum, PGAcademicPathWayEnum, RoleEnum
from pace_project.paceapp.models import University, Course, Country, UniBoardGap, Board, UniversityStateMapping, State, \
    EntryCriteria, EnglishTest, PGEntryCriteria, Campus, Stream, SubStream, Level, Year, Intake, Region, \
    UniversityIntake
from pace_project.paceapp.utils import get_student_academic_form_layout, get_english_test_form_layout
from pace_project.users.models import Partner, PartnerBranch, Student, UGStudentAcademic, PGStudentAcademic, \
    PartnerCommunication, Employee, User
from pace_project.utils.utils import get_partner_role_obj
from pace_project.utils.validators import validate_unique_legal_name


class YearForm(forms.ModelForm):
    class Meta:
        model = Year
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(YearForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('intake_year', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class UniversityForm(forms.ModelForm):
    is_active = forms.BooleanField(widget=forms.CheckboxInput(), initial=True, required=False)

    class Meta:
        model = University
        fields = "__all__"
        required = True

    def __init__(self, *args, **kwargs):
        super(UniversityForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_university=True)
        self.fields['logo'].label = "Choose university logo"
        self.fields['email'].required = True
        self.fields['application_accepting_from'].required = True
        self.fields['country'].empty_label = "Select a country"
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('name', css_class='col-md-6'),
                Div('alis', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                Div('campus', css_class='col-md-6'),
                Div('application_accepting_from', css_class='col-md-6'),
                Div('color_code', css_class='col-md-4'),
                Div('commission_frequency', css_class='col-md-4'),
                Div('logo', css_class='col-md-4'),
                Div(
                    Div('partially_1', css_class='col-md-4'),
                    Div('partially_2', css_class='col-md-4'),
                    Div('priority', css_class='col-md-4'),
                    css_class='row partially-fields'
                ),
                Div('is_active', css_class='col-md-4'),
                Div('is_premium', css_class='col-md-4'),
                css_class='row',
            ),
        )

        self.helper.form_tag = False
        self.helper.disable_csrf = True


class UniversityStateMappingForm(forms.ModelForm):
    is_active = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    class Meta:
        model = UniversityStateMapping
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_university = self.initial.get('university')
        if initial_university:
            active_ap_accepting_countries = initial_university.application_accepting_from.filter(is_active=True)
            self.fields['boards'].queryset = Board.objects.filter(
                country__in=active_ap_accepting_countries, is_active=True
            )
            self.fields['states'].queryset = State.objects.filter(
                country__in=active_ap_accepting_countries, is_active=True
            )

        self.fields['university'].widget = forms.HiddenInput()

        self.fields['boards'].empty_label = "Select a board"
        self.fields['boards'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['states'].empty_label = "Select a state"
        self.fields['states'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['streams'].empty_label = "Select a Stream"
        self.fields['streams'].widget.attrs.update({'data-searchable': 'true'})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('boards', css_class='col-md-6'),
                Div('states', css_class='col-md-6'),
                Div('streams', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                Div('university', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class UBSSMappingUpdateForm(UniversityStateMappingForm):
    """University board state stream mapping update form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UniBoardGapForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_university = self.initial.get('university')
        if initial_university:
            unique_uniset = UniversityStateMapping.objects.filter(university=initial_university, is_active=True)

            distinct_board_ids = unique_uniset.values('boards').distinct()
            distinct_state_ids = unique_uniset.values('states').distinct()

            # Now, construct querysets for Board and State models based on the distinct IDs
            unique_boards_queryset = Board.objects.filter(pk__in=distinct_board_ids)
            unique_states_queryset = State.objects.filter(pk__in=distinct_state_ids)

            self.fields['board'].queryset = unique_boards_queryset
            self.fields['state'].queryset = unique_states_queryset

        self.fields['university'].widget = forms.HiddenInput()
        self.fields['board'].empty_label = "Select a board"
        self.fields['board'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['state'].empty_label = "Select a state"
        self.fields['state'].widget.attrs.update({'data-searchable': 'true'})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('board', css_class='col-md-5'),
                Div('state', css_class='col-md-5'),
                Div('gap', css_class='col-md-2'),
                Div('university', css_class='col-md-1'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = UniBoardGap
        fields = ('university', 'board', 'state', 'gap')


class CourseForm(forms.ModelForm):
    is_active = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    class Meta:
        model = Course
        fields = [
            'country', 'university', 'name',
            'level', 'substream', 'stream', 'intake', 'link', 'tuition_fees', 'scholarship',
            'campus',
            'entry_requirement', 'is_active'
        ]

        widgets = {
            'link': forms.Textarea(attrs={'placeholder': 'Add course link', 'rows': 3}),
            'tuition_fees': forms.Textarea(attrs={'placeholder': 'Enter tuition fees', 'rows': 3}),
            'scholarship': forms.Textarea(attrs={'placeholder': 'Enter scholarship', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter active countries
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_university=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'
        self.fields['level'].empty_label = 'Select a level'
        self.fields['stream'].empty_label = 'Select stream'
        self.fields['link'].label = 'Course link'
        self.fields['link'].widget.attrs['placeholder'] = 'Add course link'
        self.fields['tuition_fees'].widget.attrs['placeholder'] = 'Enter tuition fees'
        self.fields['scholarship'].widget.attrs['placeholder'] = 'Enter scholarship'
        self.fields['substream'].empty_label = 'Select substream'
        self.fields['intake'].empty_label = 'Select intake'
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-4'),
                Div('university', css_class='col-md-4'),
                Div('level', css_class='col-md-4'),
                Div('stream', css_class='col-md-4'),
                Div('substream', css_class='col-md-4'),
                Div('name', css_class='col-md-4'),
                Div('link', css_class='col-md-4'),
                Div('tuition_fees', css_class='col-md-4'),
                Div('scholarship', css_class='col-md-4'),
                Div('campus', css_class='col-md-4'),
                Div('intake', css_class='col-md-4'),
                # Div('entry_requirement', css_class='col-md-12'),
                Div('is_active', css_class='col-md-4'),
                css_class='row',
            ),
        )
        self.helper.disable_csrf = True


class UpdateCourseForm(CourseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'] = forms.BooleanField(required=False)


class CountryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country_name', css_class='col-md-6'),
                Div('country_code', css_class='col-md-6'),
                Div('country_currency', css_class='col-md-6'),
                Div('country_currency_symbol', css_class='col-md-6'),
                Div('commission_frequency', css_class='col-md-6'),
                Div('country_logo', css_class='col-md-6'),
                Div('priority', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                Div('is_active_for_student', css_class='col-md-6'),
                Div('is_active_for_university', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = Country
        fields = '__all__'


class EntryCriteriaForm(forms.ModelForm):
    class Meta:
        model = EntryCriteria
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            self._update_fields(instance)

        self.fields['course'].widget.attrs.update({'readonly': True})
        self.fields['course'].required = False

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('course', css_class='col-md-6'),
                Div('country', css_class='col-md-6'),
                Div('board', css_class='col-md-6'),
                Div('tenth_math_marks', css_class='col-md-6'),
                Div('twelfth_math_marks', css_class='col-md-6'),
                Div('twelfth_english_marks', css_class='col-md-6'),
                Div('overall_marks', css_class='col-md-6'),
                Div('best_four_marks', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def _update_fields(self, instance):
        university = instance.course.university

        # Filter boards based on the related university
        unique_board_ids = UniversityStateMapping.objects.filter(
            university=university, is_active=True
        ).values_list('boards', flat=True).distinct()
        unique_boards = Board.objects.filter(pk__in=unique_board_ids)
        self.fields['board'].queryset = unique_boards

        # Filter countries based on the related university
        accepting_countries = university.application_accepting_from.filter(is_active=True)
        self.fields['country'].queryset = accepting_countries


class EnglishTestForm(forms.ModelForm):
    class Meta:
        model = EnglishTest
        fields = '__all__'
        exclude = ['course', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('type', css_class='col-md-4'),
                Div('overall', css_class='col-md-4'),
                Div('speaking', css_class='col-md-4'),
                Div('listening', css_class='col-md-4'),
                Div('writing', css_class='col-md-4'),
                Div('reading', css_class='col-md-4'),
                Div('is_active', css_class='col-md-4'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PGEntryCriteriaForm(forms.ModelForm):
    class Meta:
        model = PGEntryCriteria
        fields = '__all__'
        exclude = ['course', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('board', css_class='col-md-6'),
                Div('twelfth_english_marks', css_class='col-md-6'),
                Div('diploma_overall_marks', css_class='col-md-6'),
                Div('ug_overall_marks', css_class='col-md-6'),
                Div('level_diploma_marks', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class BoardForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 5, }), required=False)

    class Meta:
        model = Board
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_student=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('name', css_class='col-md-6'),
                Div('description', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ['name', 'country', 'region', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_student=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'
        self.fields['region'].empty_label = 'Select a region'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-4'),
                Div('region', css_class='col-md-4'),
                Div('name', css_class='col-md-4'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['country', 'name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_student=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('name', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class CampusForm(forms.ModelForm):
    class Meta:
        model = Campus
        fields = ['name', 'country', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.filter(is_active=True, is_active_for_university=True)
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('country', css_class='col-md-6'),
                Div('name', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['stream', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('stream', css_class='col-md-6'),
                Div('is_active', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class SubStreamForm(forms.ModelForm):
    stream = forms.ModelChoiceField(queryset=Stream.objects.filter(is_active=True))

    class Meta:
        model = SubStream
        fields = ['sub_stream_name', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('stream', css_class='col-md-6'),
                Div('sub_stream_name', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('level', css_class='col-md-6'),
                Div('streams', css_class='col-md-6'),
                Div('boards', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PartnerForm(SignupForm):
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
        max_length=255,
        label="Company Name",
        widget=forms.TextInput(attrs={"placeholder": "Company Name"})
    )
    legal_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Registered Company Name"}),
        label="Registered Company Name", required=False
    )
    designation = forms.CharField(required=False)
    company_type = forms.ChoiceField(
        choices=COMPANY_TYPE_CHOICES, widget=forms.Select(attrs={'data-searchable': 'true'}), required=False
    )

    contact_name = forms.CharField(required=False, label="Name")
    email = forms.EmailField()
    mobile_country_code = forms.ModelChoiceField(
        queryset=Country.objects.all(), empty_label="Select a country", label="Country Code"
    )
    mobile_number = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': 'Mobile Number'}))

    whatsapp_country_code = forms.ModelChoiceField(
        required=False, label="Country Code",
        queryset=Country.objects.all(), empty_label="Select a country"
    )
    whatsapp_number = forms.CharField(
        widget=forms.NumberInput(attrs={'placeholder': 'WhatsApp Number'}), required=False
    )

    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label="Select a country")
    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="Select a state", required=False)
    city = forms.CharField(max_length=255, label="City")
    pincode = forms.CharField(widget=forms.NumberInput(), required=False)

    address = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Full Address", 'rows': 1}), label="Address", required=False
    )
    logo = forms.ImageField(label="Company Logo", required=False)
    website = forms.CharField(required=False, help_text="partner website link")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['legal_name'].validators = [lambda value: validate_unique_legal_name(value, instance=self.instance)]
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'

        self.fields['mobile_country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['whatsapp_country_code'].widget.attrs.update({'data-searchable': 'true'})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('company_name', css_class='col-md-3'),
                Div('legal_name', css_class='col-md-3'),
                Div('contact_name', css_class='col-md-3'),
                Div('designation', css_class='col-md-3'),
                Div('email', css_class='col-md-3'),

                Div('mobile_country_code', css_class='col-md-3'),
                Div('mobile_number', css_class='col-md-3'),
                Div('whatsapp_country_code', css_class='col-md-3'),
                Div('whatsapp_number', css_class='col-md-3'),
                Div('company_type', css_class='col-md-3'),

                Div('country', css_class='col-md-3'),
                Div('state', css_class='col-md-3'),
                Div('city', css_class='col-md-3'),
                Div('pincode', css_class='col-md-3'),
                Div('address', css_class='col-md-6'),
                Div('logo', css_class='col-md-3'),
                Div('website', css_class='col-md-3'),
                Div('password1', css_class='col-md-3'),
                Div('password2', css_class='col-md-3'),
                css_class="row"
            )
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def save(self, request):
        email = self.cleaned_data.get("email")
        if self.account_already_exists:
            raise ValueError(email)
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self, commit=False)
        self.custom_signup(request, user)
        primary = setup_user_email(request, user, [EmailAddress(email=email)] if email else [])
        primary.verified = True
        primary.save()
        return user

    def custom_signup(self, request, user):
        super().custom_signup(request, user)
        try:
            user.role = get_partner_role_obj()
            company_name = self.cleaned_data.get("company_name")
            logo = self.cleaned_data.get("logo")
            user.name = company_name
            if logo:
                user.avatar = logo
            user.save()
            self.save_partner(user, request.user)
        except Exception as e:
            print("custom signup exception call ", e)

    def save_partner(self, user, logged_in_user):
        partner = Partner.objects.create(
            user=user,
            company_name=self.cleaned_data.get('company_name'),
            legal_name=self.cleaned_data.get('legal_name'),
            contact_name=self.cleaned_data.get('contact_name'),
            email=self.cleaned_data.get('email'),

            mobile_country_code=self.cleaned_data.get('mobile_country_code'),
            mobile_number=self.cleaned_data.get('mobile_number'),
            whatsapp_country_code=self.cleaned_data.get('whatsapp_country_code'),
            whatsapp_number=self.cleaned_data.get('whatsapp_number'),

            company_type=self.cleaned_data.get('company_type'),
            website=self.cleaned_data.get('website'),
            designation=self.cleaned_data.get('designation'),

            country=self.cleaned_data.get('country'),
            state=self.cleaned_data.get('state'),
            city=self.cleaned_data.get('city'),
            pincode=self.cleaned_data.get('pincode'),
            address=self.cleaned_data.get('address'),

            is_active=True,
            onboarding_completed=True,
            on_boarded_by=logged_in_user
        )
        return partner


class UserLogoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']


class PartnerBranchForm(forms.ModelForm):
    class Meta:
        model = PartnerBranch
        fields = '__all__'
        exclude = ['partner', 'is_head_office']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({'cols': 5, 'rows': 2})
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'
        self.fields['state'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['state'].empty_label = 'Select a state'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('country', css_class='col-md-6'),
                Div('state', css_class='col-md-6'),
                Div('city', css_class='col-md-6'),
                Div('pincode', css_class='col-md-6'),
                Div('is_active', css_class='col-md-3'),
                Div('is_head_office', css_class='col-md-3'),
                Div('address', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PartnerCommunicationForm(forms.ModelForm):
    class Meta:
        model = PartnerCommunication
        fields = ['communication_type', 'communication_value', 'country_code', 'branch']

    def __init__(self, *args, **kwargs):
        super(PartnerCommunicationForm, self).__init__(*args, **kwargs)
        partner = self.initial.get('partner')
        if partner:
            self.fields['branch'].queryset = partner.partnerbranch_set.all()

        placeholder_choice = ('', 'Select Contact Type')
        self.fields['communication_type'].choices = [placeholder_choice] + [
            choice for choice in self.fields['communication_type'].choices if choice[0]
        ]

        self.fields['communication_type'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['communication_type'].label = 'Contact Type'
        self.fields['country_code'].empty_label = 'Select Country Code'
        self.fields['country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['branch'].empty_label = 'Select Branch'
        self.fields['branch'].widget.attrs.update({'data-searchable': 'true'})

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('communication_type', css_class='col-md-6'),
                Div('country_code', css_class='col-md-6'),
                Div('communication_value', css_class='col-md-6'),
                Div('branch', css_class='col-md-6'),
                css_class='row',
            ),

        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class StudentForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }), required=False)

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['is_active', 'created_by', 'assessment_status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['partner'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['partner'].empty_label = 'Choose Partner/Agent'

        self.fields['study_country'].empty_label = 'Select Study Country'
        self.fields['study_country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['study_country'].required = True

        self.fields['study_level'].empty_label = 'Select Study Level'
        self.fields['study_level'].required = True
        self.fields['date_of_birth'].required = True

        self.fields['type'].required = False
        self.fields['type'].label = "Student Type"

        if not user is None:
            if user.is_superuser:
                self.fields['study_country'].queryset = Country.objects.all()
            else:
                employee = Employee.objects.filter(user=user).first()
                if employee:
                    assigned_country = employee.assigned_country
                    if assigned_country:
                        self.fields['study_country'].queryset = Country.objects.filter(id=assigned_country.id)
                        self.fields['study_country'].initial = assigned_country
                        country_specific_level = CountrySpecificLevel.objects.filter(
                            country=assigned_country, is_active=True
                        ).first()
                        if country_specific_level:
                            self.fields['study_level'].queryset = country_specific_level.levels.all()
                        else:
                            self.fields['study_level'].queryset = Level.objects.none()
                    else:
                        self.fields['study_level'].queryset = Level.objects.none()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('partner', css_class='col-md-3'),
                Div('first_name', css_class='col-md-3'),
                Div('middle_name', css_class='col-md-3'),
                Div('last_name', css_class='col-md-3'),
                Div('passport_number', css_class='col-md-3'),
                Div('date_of_birth', css_class='col-md-3'),
                Div('email', css_class='col-md-3'),
                Div('mobile_number', css_class='col-md-3'),
                Div('type', css_class='col-md-3'),
                Div('study_country', css_class='col-md-3'),
                Div('study_level', css_class='col-md-3'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class UGStudentAcademicForm(forms.ModelForm):
    class Meta:
        model = UGStudentAcademic
        fields = '__all__'
        exclude = ['student', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['work_experience'].widget.attrs.update({'placeholder': 'Enter work experience if any'})
        if self.instance:
            instance = self.instance
            self.fields['board'].queryset = instance.student.study_level.boards.filter(
                is_active=True, country=instance.country
            )
            self.fields['state'].queryset = State.objects.filter(is_active=True, country=instance.country)
            self.fields['stream'].queryset = instance.student.study_level.streams.filter(is_active=True)

            if self.instance.academic_pathway == UGAcademicPathWayEnum.DIPLOMA.value:
                self.fields.pop('twelfth_math_marks')
                self.fields.pop('twelfth_best_four_marks')
                self.fields.pop('twelfth_english_marks')
                self.fields['overall_marks'].label = "Diploma Overall %"
            if self.instance.academic_pathway == UGAcademicPathWayEnum.INTERMEDIATE.value:
                self.fields['overall_marks'].label = "12th Overall %"

        self.fields['state'].widget.attrs.update({'data-searchable': 'true'})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                *get_student_academic_form_layout(),
                Div('overall_marks', css_class='col-md-6'),
                Div('twelfth_math_marks', css_class='col-md-6'),
                Div('twelfth_english_marks', css_class='col-md-6'),
                Div('twelfth_best_four_marks', css_class='col-md-6'),
                Div('work_experience', css_class='col-md-6'),
                Div(css_class='w-100'),
                *get_english_test_form_layout(),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class PGStudentAcademicForm(forms.ModelForm):
    class Meta:
        model = PGStudentAcademic
        fields = '__all__'
        exclude = ['student', 'tenth_marks', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['work_experience'].widget.attrs.update({'placeholder': 'Enter work experience if any'})
        self.fields['ug_overall_marks'].label = "UG Overall %"
        self.fields['level_diploma_marks'].label = "Level Diploma Overall %"
        if self.instance:
            instance = self.instance

            self.fields['board'].queryset = instance.student.study_level.boards.filter(
                is_active=True, country=instance.country
            )
            self.fields['state'].queryset = State.objects.filter(is_active=True, country=instance.country)
            self.fields['stream'].queryset = instance.student.study_level.streams.filter(is_active=True)

            if instance.academic_pathway == PGAcademicPathWayEnum.INTERMEDIATE_UG.value:
                self.fields.pop('level_diploma_marks')
                self.fields.pop('diploma_overall_marks')
                self.fields['twelfth_english_marks'].label = "12th English Marks"

            elif instance.academic_pathway == PGAcademicPathWayEnum.DIPLOMA_UG.value:
                self.fields['diploma_overall_marks'].label = 'Diploma Overall %'
                self.fields.pop('level_diploma_marks')
                self.fields.pop('twelfth_english_marks')

            elif instance.academic_pathway == PGAcademicPathWayEnum.LEVEL_DIPLOMA.value:
                self.fields.pop('diploma_overall_marks')
                self.fields.pop('ug_overall_marks')
                self.fields.pop('twelfth_english_marks')

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                *get_student_academic_form_layout(),
                Div('twelfth_english_marks', css_class='col-md-6'),
                Div('diploma_overall_marks', css_class='col-md-6'),
                Div('ug_overall_marks', css_class='col-md-6'),
                Div('level_diploma_marks', css_class='col-md-6'),
                Div('work_experience', css_class='col-md-6'),
                Div(css_class='w-100'),
                *get_english_test_form_layout(),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class IntakeForm(forms.ModelForm):
    class Meta:
        model = Intake
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(IntakeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('intake_month', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class UniversityIntakeForm(forms.ModelForm):
    class Meta:
        model = UniversityIntake
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['university'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['university'].empty_label = 'Select University'

        self.fields['intakes'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['intakes'].empty_label = 'Select intake'
        self.fields['intakes'].required = True

        self.fields['campuses'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['campuses'].empty_label = 'Select campuses'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('university', css_class='col-md-4'),
                Div('intakes', css_class='col-md-4'),
                Div('campuses', css_class='col-md-4'),
                Div('is_active', css_class='col-md-8'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class GenericDocumentForm(forms.ModelForm):
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


class PartnerOnBoardingRequestForm(forms.ModelForm):
    COMPANY_TYPE_CHOICES = [
        ('', 'Select a company type'),
        ('Proprietorship', 'Proprietorship'),
        ('Partnership', 'Partnership'),
        ('Pvt. Limited', 'Pvt. Limited'),
        ('Public', 'Public'),
        ('LLP', 'LLP'),
        ('Limited', 'Limited'),
    ]
    IS_ANY_BRANCH_CHOICES = [
        (False, 'No'),
        (True, 'Yes'),

    ]
    is_any_branch = forms.ChoiceField(
        choices=IS_ANY_BRANCH_CHOICES, required=False, widget=forms.Select(attrs={'data-searchable': 'true'})
    )
    # date_of_commencement = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }), required=False)
    company_type = forms.ChoiceField(
        choices=COMPANY_TYPE_CHOICES, required=True, widget=forms.Select(attrs={'data-searchable': 'true'})
    )
    remark = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 5, }), required=False)

    class Meta:
        model = PartnerOnBoardingRequest
        fields = '__all__'
        exclude = ('office_type', 'is_active', 'status', 'on_boarded_by',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['country'].empty_label = 'Select a country'
        self.fields['country'].required = True
        self.fields['company_name'].widget.attrs.update({'placeholder': 'Company Name'})
        self.fields['company_name'].label = 'Company Name'

        self.fields['legal_name'].widget.attrs.update({'placeholder': 'Registered Company Name'})
        self.fields['legal_name'].label = 'Registered Company Name'
        self.fields['legal_name'].required = False
        self.fields['legal_name'].validators = [lambda value: validate_unique_legal_name(value, instance=self.instance)]

        self.fields['owner_name'].widget.attrs.update({'placeholder': 'Owner Name'})
        self.fields['owner_name'].required = True
        self.fields['owner_email'].required = True
        self.fields['owner_mobile_number'].required = True
        self.fields['contact_name'].required = True
        self.fields['owner_email'].widget.attrs.update({'placeholder': 'Owner Email'})
        self.fields['owner_mobile_number'].widget = forms.NumberInput(attrs={'placeholder': 'Owner Mobile Number'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
        self.fields['email'].required = True

        self.fields['mobile_number'].widget = forms.NumberInput(attrs={'placeholder': 'Mobile Number'})
        self.fields['whatsapp_number'].widget = forms.NumberInput(attrs={'placeholder': 'WhatsApp Number'})

        self.fields['address'].widget.attrs.update({'placeholder': 'Full Address'})
        self.fields['state'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['state'].empty_label = 'Select a state'
        self.fields['pincode'].widget = forms.NumberInput()
        self.fields['number_of_branch'].widget = forms.NumberInput()
        self.fields['target_for_next_intake'].widget = forms.NumberInput()

        self.fields['mobile_country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['whatsapp_country_code'].widget.attrs.update({'data-searchable': 'true'})

        self.fields['mobile_country_code'].empty_label = 'Select a country'
        self.fields['whatsapp_country_code'].empty_label = 'Select a country'

        self.fields['mobile_country_code'].label = 'Country code'
        self.fields['whatsapp_country_code'].label = 'Country code'
        self.fields['mobile_country_code'].label_from_instance = lambda \
                obj: f"{obj.country_code}-{obj.country_name}" if obj.country_code and obj.country_name else '-'
        self.fields['whatsapp_country_code'].label_from_instance = lambda \
                obj: f"{obj.country_code}-{obj.country_name}" if obj.country_code and obj.country_name else '-'

        self.fields['mobile_country_code'].required = True
        self.fields['mobile_number'].required = True
        self.fields['city'].required = True

        if not user is None:
            if user.role.name == RoleEnum.REGIONAL_MARKETING_HEAD.value:
                self.fields['onboarding_completed'].widget = forms.HiddenInput()

        self.helper.layout = Layout(
            Div(
                Div('company_name', css_class='col-md-3'),
                Div('legal_name', css_class='col-md-3'),
                Div('owner_name', css_class='col-md-3'),
                Div('owner_email', css_class='col-md-3'),
                Div('owner_mobile_number', css_class='col-md-3'),
                Div('contact_name', css_class='col-md-3'),
                Div('email', css_class='col-md-3'),
                Div('mobile_country_code', css_class='col-md-3'),
                Div('mobile_number', css_class='col-md-3'),
                Div('whatsapp_country_code', css_class='col-md-3'),
                Div('whatsapp_number', css_class='col-md-3'),
                Div('company_type', css_class='col-md-3'),
                Div('country', css_class='col-md-3'),
                Div('state', css_class='col-md-3'),
                Div('city', css_class='col-md-3'),
                Div('pincode', css_class='col-md-3'),
                Div('address', css_class='col-md-3'),
                # Div('date_of_commencement', css_class='col-md-3'),
                Div('logo', css_class='col-md-3'),
                Div('website', css_class='col-md-3'),
                Div('is_any_branch', css_class='col-md-3'),

                Div('number_of_branch', css_class='col-md-3'),
                Div('target_for_next_intake', css_class='col-md-3'),

                Div('remark', css_class='col-md-6'),
                Div('onboarding_completed', css_class='col-md-3'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class DailyProgressReportForm(forms.ModelForm):
    activity_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', }), required=True)

    class Meta:
        model = DailyProgressReport
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['created_by'].widget = forms.HiddenInput()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('activity_date', css_class='col-md-6'),
                Div('task_partner', css_class='col-md-6'),
                Div('created_by', css_class='col-md-6'),
                Div('activity_description', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True
