from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from pace_project.core.models.core_models import Webinar
from pace_project.meetcom.forms import MeetingForms, RMMeetingForms, WebinarForms
from pace_project.meetcom.models import Meeting
from pace_project.paceapp.models import University


class MeetingListView(ListView):
    model = Meeting
    template_name = "meetcom/meeting/meeting_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        subject = self.request.GET.get('subject')
        description = self.request.GET.get('description')
        scheduled_date = self.request.GET.get('scheduled_date')
        assigned_to = self.request.GET.get('assigned_to')
        created_by = self.request.GET.get('created_by')

        if subject:
            queryset = queryset.filter(subject__icontains=subject)

        if description:
            queryset = queryset.filter(description__icontains=description)

        if scheduled_date:
            queryset = queryset.filter(scheduled_date=scheduled_date)

        if assigned_to:
            queryset = queryset.filter(assigned_to__username__icontains=assigned_to)

        if created_by:
            queryset = queryset.filter(created_by__username__icontains=created_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Meeting.STATUS_CHOICES
        return context


class MeetingCreateView(CreateView):
    model = Meeting
    form_class = MeetingForms
    template_name = "meetcom/meeting/_form.html"

    def form_valid(self, form):
        meeting = form.save(commit=False)
        meeting.created_by = self.request.user
        meeting.save()
        form.save_m2m()  # Save the many-to-many data for the form
        messages.success(self.request, 'Meeting was successfully created.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('meetcom:meeting_list')


class MeetingUpdateView(UpdateView):
    model = Meeting
    form_class = MeetingForms
    template_name = "meetcom/meeting/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Meeting has been successfully updated!')
        return reverse('meetcom:meeting_list')


class MeetingDeleteView(DeleteView):
    model = Meeting
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Meeting Deleted Successfully!')
        return reverse("meetcom:meeting_list")


class MeetingDetailView(DetailView):
    model = Meeting
    template_name = "meetcom/meeting/meeting_detail.html"


class RMMeetingCreateView(CreateView):
    model = Meeting
    form_class = RMMeetingForms
    template_name = 'meetcom/rm_meeting/_form.html'

    def form_valid(self, form):
        meeting = form.save(commit=False)
        meeting.created_by = self.request.user
        meeting.save()
        form.save_m2m()  # Save the many-to-many data for the form
        messages.success(self.request, 'Meeting was successfully created.')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(RMMeetingCreateView, self).get_form_kwargs()
        kwargs['employee'] = self.request.user.employee
        return kwargs

    def get_success_url(self):
        return reverse('meetcom:rm_meeting_list')


class RMMeetingListView(ListView):
    model = Meeting
    template_name = 'meetcom/rm_meeting/_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(created_by=self.request.user).order_by('-created')
        subject = self.request.GET.get('subject')
        description = self.request.GET.get('description')
        scheduled_date = self.request.GET.get('scheduled_date')
        assigned_to = self.request.GET.get('assigned_to')
        created_by = self.request.GET.get('created_by')

        if subject:
            queryset = queryset.filter(subject__icontains=subject)

        if description:
            queryset = queryset.filter(description__icontains=description)

        if scheduled_date:
            queryset = queryset.filter(scheduled_date__date=scheduled_date)

        if assigned_to:
            queryset = queryset.filter(assigned_to__name__icontains=assigned_to)

        if created_by:
            queryset = queryset.filter(created_by__name__icontains=created_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Meeting.STATUS_CHOICES
        return context


class RMMeetingDeleteView(DeleteView):
    model = Meeting
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Meeting Deleted Successfully!')
        return reverse('meetcom:rm_meeting_list')


class RMMeetingUpdateView(UpdateView):
    model = Meeting
    form_class = RMMeetingForms
    template_name = "meetcom/rm_meeting/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Meeting has been successfully updated!')
        return reverse('meetcom:rm_meeting_list')


class RMMeetingDetailView(DetailView):
    model = Meeting
    template_name = "meetcom/rm_meeting/_detail.html"


class WebinarCreateView(CreateView):
    model = Webinar
    form_class = WebinarForms
    template_name = 'meetcom/webinar/_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['created_by'] = self.request.user
        return initial

    def get_success_url(self):
        messages.success(self.request, 'Webinar is successfully created.')
        return reverse('meetcom:webinar_list')


class WebinarListView(ListView):
    model = Webinar
    template_name = 'meetcom/webinar/_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        webinar_for = self.request.GET.get('webinar_for')
        scheduled_date = self.request.GET.get('scheduled_date')
        university = self.request.GET.get('university')
        status = self.request.GET.get('status')

        if webinar_for:
            queryset = queryset.filter(webinar_for__icontains=webinar_for)

        if scheduled_date:
            queryset = queryset.filter(schedule__date=scheduled_date)

        if university:
            queryset = queryset.filter(university_id=university)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['university'] = University.objects.all()
        return ctx
