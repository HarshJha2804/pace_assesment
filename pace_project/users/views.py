from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, View
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.views.generic.edit import FormMixin
from django.contrib import messages

from pace_project.core.forms import FollowUpForm
from pace_project.paceapp.enums import RoleEnum
from pace_project.paceapp.forms import PartnerForm, UserLogoForm
from pace_project.paceapp.models import Year
from pace_project.users.enums import PartnerStatusEnum
from pace_project.users.models import User, Partner, Role, UGStudentAcademic, Student, PGStudentAcademic
from pace_project.users.services import add_ug_student_academics, add_pg_student_academics


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


@login_required
def upload_logo_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserLogoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:detail', pk=user.pk)
    else:
        form = UserLogoForm(instance=user)
    return render(request, 'users/upload_avatar.html', {'form': form, 'object': user})


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name", "avatar"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        # for mypy to know that the user is authenticated
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        user = self.request.user
        return reverse("users:detail", kwargs={"pk": user.pk})


user_redirect_view = UserRedirectView.as_view()


class PartnerFollowUpView(FormMixin, DetailView):
    model = Partner
    form_class = FollowUpForm
    template_name = "paceapp/partner/follow_up_form.html"

    def get_initial(self):
        initials = super().get_initial()
        partner_object = self.get_object()
        initials['content_type'] = ContentType.objects.get_for_model(Partner)
        initials['object_id'] = partner_object.id
        return initials

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        follow_up_instance = form.save(commit=False)
        follow_up_instance.assigned_to = self.request.user
        follow_up_instance.created_by = self.request.user
        follow_up_instance.save()
        if self.object.status != PartnerStatusEnum.FOLLOW_UP.value:
            self.object.status = PartnerStatusEnum.FOLLOW_UP.value
            self.object.save(update_fields=['status', 'modified'])

        messages.success(self.request, "Follow-up set successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url


def mark_partner_not_interested_view(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == "POST":
        confirmation = request.POST.get("confirmation")
        if confirmation == "Confirm":
            partner.status = PartnerStatusEnum.NOT_INTERESTED.value
            partner.save(update_fields=["status", "modified"])
            messages.success(request, "Partner has been marked as not interested!")
        else:
            messages.warning(request, "Incorrect confirmation!")
        return redirect(partner.get_absolute_url)

    return HttpResponse("Invalid method!")


def mark_partner_interested_view(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == "POST":
        confirmation = request.POST.get("confirmation")
        if confirmation == "Confirm":
            partner.status = PartnerStatusEnum.INTERESTED.value
            partner.is_active = True
            partner.save(update_fields=["status", "is_active", "modified"])
            messages.success(request, "Partner has been marked as interested!")
        else:
            messages.warning(request, "Incorrect confirmation!")
        return redirect(partner.get_absolute_url)
    else:
        return HttpResponse("Invalid method!")


def add_ug_student_academic_view(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if UGStudentAcademic.objects.filter(student=student).exists():
        messages.warning(request, f"{student} (Academic) has already been added.")
        return redirect(student.get_absolute_url)

    if request.method == "POST":
        form_data = request.POST
        add_ug_student_academics(student=student, form_data=form_data)
        messages.success(request, "Academic details added successfully!")
        return redirect(student.get_absolute_url)

    years = Year.objects.filter(is_active=True)
    context = {'student': student, 'years': years}
    return render(request, "student/add_ug_student_academic_form.html", context)


def add_pg_student_academic_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if PGStudentAcademic.objects.filter(student=student).exists():
        messages.warning(request, f"{student} (Academic) has already been added.")
        return redirect(student.get_absolute_url)

    if request.method == "POST":
        form_data = request.POST
        add_pg_student_academics(student=student, form_data=form_data)
        messages.success(request, "Academic details added successfully!")
        return redirect(student.get_absolute_url)

    years = Year.objects.filter(is_active=True)
    context = {'student': student, 'years': years}
    return render(request, "student/add_pg_student_academic_form.html", context)
