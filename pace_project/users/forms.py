from allauth.account.forms import SignupForm, BaseSignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django.contrib.auth import forms as admin_forms, get_user_model
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _
from django import forms
from pace_project.users.models import Employee, Role, ApplicationManager
from pace_project.paceapp.models import Country, University, Region

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Role Name"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('description', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class InternalUserForm(SignupForm):
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True))
    name = forms.CharField(label=_("Name"))
    is_staff = forms.BooleanField(label=_("Staff"), required=False)
    is_active = forms.BooleanField(label=_("Active"), required=False, initial=True)
    avatar = forms.ImageField(label=_("Avatar"), required=False)

    def save(self, request, commit=True):
        user = super().save(request)
        user.name = self.cleaned_data.get('name')
        user.role = self.cleaned_data.get('role')
        password = self.cleaned_data["password1"]
        if commit:
            user.set_password(password)
            user.save()
        return user

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def __init__(self, *args, **kwargs):
        super(InternalUserForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['role'].empty_label = "Select Role"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                Div('role', css_class='col-md-6'),
                Div('avatar', css_class='col-md-6'),
                Div('is_staff', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                Div('password1', css_class='col-md-6'),
                Div('password2', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class EmployeeForm(InternalUserForm):
    mobile_country_code = forms.ModelChoiceField(queryset=Country.objects.all(), label=_("Country Code"))
    mobile_number = forms.CharField(
        label=_("Mobile Number"), max_length=20, widget=forms.NumberInput(attrs={'placeholder': 'Mobile Number'})
    )
    whatsapp_country_code = forms.ModelChoiceField(
        queryset=Country.objects.all(), label=_("Country Code"), required=False
    )
    whatsapp_number = forms.CharField(
        label=_("WhatsApp Number"), max_length=20, required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'WhatsApp Number'})
    )
    emergency_mobile_number = forms.CharField(
        label=_("Emergency Mobile Number"), max_length=20, required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Emergency Mobile Number'})
    )
    emergency_contact_relation = forms.ChoiceField(
        choices=[], label=_("Emergency Contact Relation"), required=False
    )
    assigned_country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True, is_active_for_university=True), label="Assign Country")
    assigned_universities = forms.ModelMultipleChoiceField(
        queryset=University.objects.filter(is_active=True), label="Assign University",
        required=False
    )
    is_head = forms.BooleanField(required=False, label="Is Head")

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Full Name'})
        self.fields['mobile_country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['whatsapp_country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['assigned_country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['emergency_mobile_number'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['emergency_contact_relation'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['emergency_contact_relation'].choices = [('',
                                                              'Select Emergency Contact Relation')] + Employee.EMERGENCY_CONTACT_RELATION_CHOICES
        self.fields['emergency_contact_relation'].empty_label = 'Select Emergency Contact Relation'
        self.fields['assigned_country'].empty_label = 'Select Country'
        self.fields['mobile_country_code'].empty_label = 'Select Country'
        self.fields['whatsapp_country_code'].empty_label = 'Select Country'
        self.fields['role'].empty_label = 'Select Role'
        self.fields['assigned_universities'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['assigned_universities'].empty_label = 'Select University'

        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                Div('mobile_country_code', css_class='col-md-2'),
                Div('mobile_number', css_class='col-md-4'),
                Div('whatsapp_country_code', css_class='col-md-2'),
                Div('whatsapp_number', css_class='col-md-4'),
                Div('emergency_mobile_number', css_class='col-md-6'),
                Div('emergency_contact_relation', css_class='col-md-6'),
                Div('role', css_class='col-md-6'),
                Div('assigned_country', css_class='col-md-6'),
                Div('assigned_universities', css_class='col-md-6'),
                Div('avatar', css_class='col-md-6'),
                Div('password1', css_class='col-md-6'),
                Div('password2', css_class='col-md-6'),
                Div('is_head', css_class='col-md-6'),
                css_class='row',
            ),
        )

    def save(self, request, commit=True):
        user = super(EmployeeForm, self).save(request, commit=False)
        user.name = self.cleaned_data.get('name')
        user.role = self.cleaned_data.get('role')
        user.is_staff = True
        user.avatar = self.cleaned_data.get('avatar')

        if commit:
            user.save()
            employee, created = Employee.objects.get_or_create(user=user)
            employee.mobile_country_code = self.cleaned_data.get('mobile_country_code')
            employee.mobile_number = self.cleaned_data.get('mobile_number')
            employee.whatsapp_country_code = self.cleaned_data.get('whatsapp_country_code')
            employee.whatsapp_number = self.cleaned_data.get('whatsapp_number')
            employee.emergency_mobile_number = self.cleaned_data.get('emergency_mobile_number')
            employee.emergency_contact_relation = self.cleaned_data.get('emergency_contact_relation')
            employee.assigned_country = self.cleaned_data.get('assigned_country')
            employee.assigned_universities.set(self.cleaned_data.get('assigned_universities'))
            employee.save()
        return user


class ApplicationManagerUpdateForm(forms.ModelForm):
    class Meta:
        model = ApplicationManager
        fields = ['is_head', 'will_process_application']


class AssignRegionForm(forms.ModelForm):
    assigned_regions = forms.ModelMultipleChoiceField(
        queryset=Region.objects.filter(is_active=True), label="Assign Regions",
    )

    class Meta:
        model = Employee
        fields = ['assigned_regions']

    def __init__(self, *ags, **kwargs):
        super(AssignRegionForm, self).__init__(*ags, **kwargs)
        self.fields['assigned_regions'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['assigned_regions'].empty_label = "Select Region"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('assigned_regions', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class EmployeeUpdateForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Name"), max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        label=_("Email"), max_length=255,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True), label=_("Role"),
    )
    avatar = forms.ImageField(
        label=_("Avatar"), required=False
    )
    mobile_country_code = forms.ModelChoiceField(queryset=Country.objects.all(), label=_("Country Code"))
    mobile_number = forms.CharField(
        label=_("Mobile Number"), max_length=20, widget=forms.NumberInput(attrs={'placeholder': 'Mobile Number'})
    )
    whatsapp_country_code = forms.ModelChoiceField(
        queryset=Country.objects.all(), label=_("Country Code"), required=False
    )
    whatsapp_number = forms.CharField(
        label=_("WhatsApp Number"), max_length=20, required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'WhatsApp Number'})
    )
    emergency_mobile_number = forms.CharField(
        label=_("Emergency Mobile Number"), max_length=20, required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Emergency Mobile Number'})
    )
    emergency_contact_relation = forms.ChoiceField(
        choices=[], label=_("Emergency Contact Relation"), required=False
    )
    assigned_country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True, is_active_for_university=True), label="Assign Country")
    assigned_universities = forms.ModelMultipleChoiceField(
        queryset=University.objects.filter(is_active=True), label="Assign University"
    )

    class Meta:
        model = Employee
        fields = [
            'mobile_country_code', 'mobile_number', 'whatsapp_country_code',
            'whatsapp_number', 'emergency_mobile_number', 'emergency_contact_relation',
            'assigned_country', 'assigned_universities', "is_head",
        ]

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)
        super(EmployeeUpdateForm, self).__init__(*args, **kwargs)

        if user_instance:
            self.fields['name'].initial = user_instance.name
            self.fields['email'].initial = user_instance.email
            self.fields['role'].initial = user_instance.role
            self.fields['avatar'].initial = user_instance.avatar

        self.fields['mobile_country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['whatsapp_country_code'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['assigned_country'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['emergency_mobile_number'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['emergency_contact_relation'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['emergency_contact_relation'].choices = [('',
                                                              'Select Emergency Contact Relation')] + Employee.EMERGENCY_CONTACT_RELATION_CHOICES
        self.fields['assigned_country'].empty_label = 'Select Country'
        self.fields['mobile_country_code'].empty_label = 'Select Country'
        self.fields['whatsapp_country_code'].empty_label = 'Select Country'
        self.fields['assigned_universities'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['assigned_universities'].empty_label = 'Select University'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                Div('mobile_country_code', css_class='col-md-2'),
                Div('mobile_number', css_class='col-md-4'),
                Div('whatsapp_country_code', css_class='col-md-2'),
                Div('whatsapp_number', css_class='col-md-4'),
                Div('emergency_mobile_number', css_class='col-md-6'),
                Div('emergency_contact_relation', css_class='col-md-6'),
                Div('role', css_class='col-md-6'),
                Div('assigned_country', css_class='col-md-6'),
                Div('assigned_universities', css_class='col-md-6'),
                Div('avatar', css_class='col-md-6'),
                Div('is_head', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def save(self, commit=True):
        employee = super(EmployeeUpdateForm, self).save(commit=False)
        user_instance = self.instance.user
        user_instance.name = self.cleaned_data.get('name')
        user_instance.email = self.cleaned_data.get('email')
        user_instance.role = self.cleaned_data.get('role')
        if 'avatar' in self.files:
            user_instance.avatar = self.cleaned_data.get('avatar')

        if commit:
            user_instance.save()
            employee.save()
        self.save_m2m()
        return employee


class UserUpdateForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True))
    name = forms.CharField(label=_("Name"))
    is_staff = forms.BooleanField(label=_("Staff"), required=False)
    is_active = forms.BooleanField(label=_("Active"), required=False)
    avatar = forms.ImageField(label=_("Avatar"), required=False)

    class Meta:
        model = User
        fields = ['name', 'email', 'role', 'avatar', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['role'].empty_label = "Select Role"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                Div('role', css_class='col-md-6'),
                Div('avatar', css_class='col-md-6'),
                Div('is_staff', css_class='col-md-6'),
                Div('is_active', css_class='col-md-6'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
