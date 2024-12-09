from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.contrib.auth import get_user_model
from django.forms.widgets import DateTimeInput

from pace_project.core.models.core_models import Webinar
from pace_project.core.models.target_models import RMTarget, RMUniversityIntake
from pace_project.meetcom.models import Meeting
from pace_project.users.models import Partner

User = get_user_model()


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"


class MeetingForms(forms.ModelForm):
    assigned_to = UserModelMultipleChoiceField(queryset=User.objects.all())

    class Meta:
        model = Meeting
        fields = ['scheduled_date', 'assigned_to', 'subject', 'description']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(MeetingForms, self).__init__(*args, **kwargs)

        self.fields['scheduled_date'].widget.attrs.update({'type': 'datetime-local'})
        self.fields['assigned_to'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['subject'].label = 'Subject'
        self.fields['description'].label = 'Description'
        self.fields['assigned_to'].empty_label = 'Select Team Members'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('subject', css_class='col-md-4'),
                Div('scheduled_date', css_class='col-md-4'),
                Div('assigned_to', css_class='col-md-4'),
                Div('description', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class RMMeetingForms(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['scheduled_date', 'assigned_to', 'subject', 'description']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super(RMMeetingForms, self).__init__(*args, **kwargs)
        if employee:
            # Assuming `Partner` has a related `User` object, you might need to adjust this part.
            active_intakes = RMUniversityIntake.objects.filter(
                rm=employee, is_active=True
            ).values('intake_id')

            self.fields['assigned_to'].queryset = User.objects.filter(
                partner__rmtarget__rm=employee,
                partner__rmtarget__intake_id__in=active_intakes,
                partner__rmtarget__is_active=True
            ).distinct()

        self.fields['scheduled_date'].widget.attrs.update({'type': 'datetime-local'})
        self.fields['assigned_to'].widget.attrs.update({'data-searchable': 'true'})
        self.fields['subject'].label = 'Subject'
        self.fields['description'].label = 'Description'
        self.fields['assigned_to'].empty_label = 'Select Team Members'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('subject', css_class='col-md-4'),
                Div('scheduled_date', css_class='col-md-4'),
                Div('assigned_to', css_class='col-md-4'),
                Div('description', css_class='col-md-12'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class WebinarForms(forms.ModelForm):
    remark = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=False)
    meeting_link = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}), required=False)

    class Meta:
        model = Webinar
        fields = '__all__'
        widgets = {
            'schedule': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(WebinarForms, self).__init__(*args, **kwargs)
        self.fields['schedule'].widget.attrs.update({'type': 'datetime-local'})
        self.fields['university'].empty_label = 'Select University'
        self.fields['created_by'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('agenda', css_class='col-md-4'),
                Div('schedule', css_class='col-md-4'),
                Div('university', css_class='col-md-4'),
                Div('webinar_for', css_class='col-md-4'),
                Div('medium', css_class='col-md-4'),
                Div('meeting_link', css_class='col-md-4'),
                Div('created_by', css_class='col-md-4'),
                Div('remark', css_class='col-md-12'),
                Div('is_active', css_class='col-md-2'),
                css_class='row',
            ),
        )
        self.helper.form_tag = False
        self.helper.disable_csrf = True
