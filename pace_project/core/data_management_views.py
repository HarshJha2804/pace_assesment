from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django_boost.views.mixins import SuperuserRequiredMixin

from pace_project.core.models.core_models import PartnerSupportDocument, CommissionStructure, UniversityInterviewStatus, \
    InterviewStatusType
from pace_project.core.forms import PartnerSupportDocumentForm, CommissionStructureForm, UniversityInterviewStatusForm, \
    InterviewStatusTypeForm, UpdateNewsForm, ContactUsForm, ReplyForm
from pace_project.paceapp.enums import RoleEnum
from pace_project.paceapp.models import Country, University, Year
from pace_project.core.models.core_models import UpdateNews
from pace_project.users.models import ContactUs, Employee, Partner, User


class AddPartnerSupportDocumentCreateView(CreateView):
    model = PartnerSupportDocument
    form_class = PartnerSupportDocumentForm
    template_name = 'core/partner_support_document/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Support Document added successfully!! ')
        return reverse('core:partner_support_document_list')


class PartnerSupportDocumentListView(ListView):
    model = PartnerSupportDocument
    paginate_by = 20
    template_name = 'core/partner_support_document/_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('intake')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(intake__intake_month__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class PartnerSupportDocumentUpdateView(UpdateView):
    model = PartnerSupportDocument
    form_class = PartnerSupportDocumentForm
    template_name = 'core/partner_support_document/update_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Support Document updated successfully!')
        return reverse('core:partner_support_document_list')


class PartnerSupportDocumentDeleteView(DeleteView):
    model = PartnerSupportDocument
    template_name = 'utils/delete_confirmation.html'

    def get_success_url(self):
        messages.success(self.request, 'Support Document deleted successfully!')
        return reverse('core:partner_support_document_list')


class AddCommissionStructureView(SuperuserRequiredMixin, CreateView):
    model = CommissionStructure
    form_class = CommissionStructureForm
    template_name = 'core/commission_structure/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Commission Structure added successfully!! ')
        return reverse('core:commission_structure_list')


class CommissionStructureListView(SuperuserRequiredMixin, ListView):
    model = CommissionStructure
    paginate_by = 20
    template_name = 'core/commission_structure/_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        country = self.request.GET.get('country_id')
        university = self.request.GET.get('university_id')
        year = self.request.GET.get('year_id')

        status = self.request.GET.get('status')

        if country:
            queryset = queryset.filter(country_id=country)

        if university:
            queryset = queryset.filter(university_id=university)

        if year:
            queryset = queryset.filter(year_id=year)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.filter(is_active=True)
        context["universities"] = University.objects.filter(is_active=True)
        context["years"] = Year.objects.filter(is_active=True)
        return context


class CommissionStructureUpdateView(SuperuserRequiredMixin, UpdateView):
    model = CommissionStructure
    form_class = CommissionStructureForm
    template_name = 'core/commission_structure/update_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Commission Structure updated successfully!')
        return reverse('core:commission_structure_list')


class CommissionStructureDeleteView(SuperuserRequiredMixin, DeleteView):
    model = CommissionStructure
    template_name = 'utils/delete_confirmation.html'

    def get_success_url(self):
        messages.success(self.request, 'Commission Structure deleted successfully!')
        return reverse('core:commission_structure_list')


class UniversityInterviewStatusListView(SuperuserRequiredMixin, ListView):
    model = UniversityInterviewStatus
    paginate_by = 20
    template_name = "core/university_interview_status/_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['universities'] = University.objects.filter(is_active=True)
        return ctx


class UniversityInterviewStatusCreateView(CreateView):
    model = UniversityInterviewStatus
    form_class = UniversityInterviewStatusForm
    template_name = 'core/university_interview_Status/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'University Interview Status added successfully!! ')
        return reverse('core:university_interview_status_list')


# Interview Status Type Module Start Here!
class InterviewStatusListView(SuperuserRequiredMixin, ListView):
    model = InterviewStatusType
    paginate_by = 20
    template_name = "core/interview_status_types/_list.html"


class InterviewStatusCreateView(SuperuserRequiredMixin, CreateView):
    model = InterviewStatusType
    form_class = InterviewStatusTypeForm
    template_name = "core/interview_status_types/_form.html"

    def get_success_url(self):
        return reverse('core:interview_status_type_list')


class InterviewStatusUpdateView(SuperuserRequiredMixin, UpdateView):
    model = InterviewStatusType
    form_class = InterviewStatusTypeForm
    template_name = 'core/interview_status_types/_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Interview Status updated successfully!')
        return reverse('core:interview_status_type_list')


class UpdatedNewsCreateView(CreateView):
    model = UpdateNews
    form_class = UpdateNewsForm
    template_name = 'paceapp/news_updates/_form.html'

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial['created_by'] = user
        return initial

    def get_success_url(self):
        messages.success(self.request, ' News Added successfully!')
        return reverse('core:news_list')


class NewsListView(ListView):
    model = UpdateNews
    paginate_by = 20
    template_name = 'paceapp/news_updates/list.html'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        return queryset


class ContactUsCreateView(CreateView):
    model = ContactUs
    form_class = ContactUsForm
    template_name = 'contactus/_form.html'

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial['send_by'] = user
        return initial

    def get_form_kwargs(self):
        """Add the logged-in user to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, 'Contact Us added successfully!')
        return reverse('partner:dashboard_partner')


class ContactUsListView(ListView):
    model = ContactUs
    paginate_by = 20
    template_name = 'contactus/list.html'

    def get_queryset(self):
        if self.request.user.role.name == RoleEnum.PARTNER_ACCOUNT_MANAGER.value:
            queryset = super().get_queryset().filter(connect_to=self.request.user)
        else:
            queryset = super().get_queryset().filter(send_by=self.request.user)
        return queryset


# class ContactUsReplyCreateView(CreateView):
#     model = ContactUs
#     template_name = 'contactus/reply_form.html'
#     form_class = ReplyForm
#
#     def get_object(self):
#         return get_object_or_404(ContactUs, id=self.kwargs['contact_us_id'])
#
#     def form_valid(self, form):
#         contact_us = get_object_or_404(ContactUs, id=self.kwargs['contact_us_id'])
#         contact_us.status = 'replied'
#         contact_us.save()
#         form.instance.send_by = self.request.user
#         form.instance.connect_to = contact_us.send_by
#         return super().form_valid(form)
#
#     def get_initial(self):
#         initial = super().get_initial()
#         contact_us = self.get_object()
#         initial['connect_to'] = contact_us.send_by
#         initial['send_by'] = self.request.user
#         return initial
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user'] = self.request.user
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['contact_us'] = self.get_object()
#         return context
#
#     def get_success_url(self):
#         messages.success(self.request, 'Reply sent successfully!')
#         return reverse('core:contact_us_list')
class ContactUsReplyCreateView(CreateView):
    model = ContactUs
    template_name = 'contactus/reply_form.html'
    form_class = ReplyForm

    def get_initial(self):
        initial = super().get_initial()
        contact_us = get_object_or_404(ContactUs, id=self.kwargs['contact_us_id'])
        initial['connect_to'] = contact_us.send_by
        initial['send_by'] = self.request.user
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, 'Reply sent successfully!')
        return reverse('core:contact_us_list')


class ReplyListView(ListView):
    model = ContactUs
    paginate_by = 20
    template_name = 'contactus/reply_list.html'
