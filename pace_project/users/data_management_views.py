from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, DetailView
from django.http import HttpResponseRedirect

from pace_project.core.models.target_models import RMTarget, RMUniversityIntake
from pace_project.paceapp.enums import RoleEnum
from pace_project.paceapp.models import Country, University, Region, Intake, Year
from pace_project.users.forms import RoleForm, InternalUserForm, EmployeeForm, AssignRegionForm, \
    ApplicationManagerUpdateForm, EmployeeUpdateForm, UserUpdateForm
from pace_project.users.models import Employee, User, Partner, ApplicationManager
from pace_project.users.models import Role
import time
from django.db import connection
from django.core.cache import cache


class UserSignupView(FormView):
    model = get_user_model()
    form_class = InternalUserForm
    template_name = "users/add_user_form.html"

    def form_valid(self, form):
        user = form.save(request=self.request)
        messages.success(self.request, "User has been added successfully !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:user_list")


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-id')
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        role = self.request.GET.get('role')
        is_staff = self.request.GET.get('staff')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if is_staff in ['True', 'False']:
            queryset = queryset.filter(is_staff=(is_staff == 'True'))

        if email:
            queryset = queryset.filter(email__icontains=email)
        if role:
            queryset = queryset.filter(role_id=role)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.all()
        return context


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/add_user_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User has been updated successfully!")
        return response

    def get_success_url(self):
        return reverse("users:user_list")


class EmployeeSignupView(FormView):
    model = get_user_model()
    form_class = EmployeeForm
    template_name = "users/employee/_form.html"

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "User has been successfully registered!")
        return reverse("users:employee_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['universities'] = list(University.objects.filter(is_active=True).values('id', 'name', 'country_id'))
        return context


class EmployeeListView(ListView):
    model = Employee
    template_name = 'users/employee_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'user', 'assigned_country', 'mobile_country_code', 'whatsapp_country_code'
        ).prefetch_related(
            'assigned_universities', 'assigned_regions'
        ).order_by('-created')

        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        whatsapp_number = self.request.GET.get('whatsapp_number')
        assigned_country = self.request.GET.get('country_id')
        status = self.request.GET.get('status')
        role = self.request.GET.get('role')

        if name:
            queryset = queryset.filter(user__name__icontains=name)
        if email:
            queryset = queryset.filter(user__email__icontains=email)

        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if whatsapp_number:
            queryset = queryset.filter(whatsapp_number__icontains=whatsapp_number)

        if assigned_country:
            queryset = queryset.filter(assigned_country_id=assigned_country)

        if role:
            queryset = queryset.filter(user__role_id=role)

        if status in ['True', 'False']:
            queryset = queryset.filter(user__is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        countries = cache.get('countries')
        if not countries:
            countries = Country.objects.all()
            cache.set('countries', countries, 3600)  # Cache for 1 hour

        roles = cache.get('roles')
        if not roles:
            roles = Role.objects.all()
            cache.set('roles', roles, 3600)  # Cache for 1 hour

        context['countries'] = countries
        context['roles'] = roles
        return context


class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = "users/employee/_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_instance'] = self.object.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        universities = list(University.objects.values('id', 'name', 'country_id'))
        context['universities'] = universities
        return context

    def get_success_url(self):
        messages.success(self.request, "Employee has been successfully updated!")
        return reverse("users:employee_list")


class EmployeeDetailView(DetailView):
    model = Employee
    template_name = 'users/employee/_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['university_intake_data'] = RMUniversityIntake.objects.filter(rm=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        employee = self.get_object()
        if 'leave' in request.POST:
            employee.is_on_leave = not employee.is_on_leave
            employee.save()
            return HttpResponseRedirect(self.request.path_info)
        return super().post(request, *args, **kwargs)


class RMListView(ListView):
    """Regional Marketing Head List view."""
    model = Employee
    paginate_by = 20
    template_name = "users/employee/_rm_list.html"

    def get_queryset(self):
        queryset = Employee.objects.regional_marketing_heads().order_by('-created')
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        whatsapp_number = self.request.GET.get('whatsapp_number')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(user__name__icontains=name)
        if email:
            queryset = queryset.filter(user__email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)
        if whatsapp_number:
            queryset = queryset.filter(whatsapp_number__icontains=whatsapp_number)
        if status in ['True', 'False']:
            queryset = queryset.filter(user__is_active=status)

        return queryset


class SetRMTargetView(DetailView):
    model = Employee
    template_name = "users/employee/_rm_set_target.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['years'] = Year.objects.current_to_future()
        ctx['partners'] = self.get_filtered_partners()
        return ctx

    def get_filtered_partners(self):
        partners = Partner.objects.none()
        region_id = self.request.GET.get('region_id')
        if region_id:
            partners = Partner.objects.filter(state__region_id=region_id)
        return partners

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        university_id = request.POST.get('university_id')
        intake_id = request.POST.get('intake_id')
        year_id = request.POST.get('year_id')
        partner_ids = self.request.POST.getlist('partner_ids')

        if not partner_ids:
            messages.warning(request, 'No partners found for the selected criteria.')
            return redirect(self.object.get_set_rm_target_url)

        self.create_rm_targets(partner_ids, university_id, intake_id, year_id)
        messages.success(request, 'Targets have been successfully added.')
        return redirect(self.object.get_rm_list_url)

    def create_rm_targets(self, partner_ids, university_id, intake_id, year_id):
        for partner_id in partner_ids:
            target_value = self.request.POST.get(f'target_p{partner_id}')
            if target_value:
                RMTarget.objects.create(
                    rm=self.object,
                    partner_id=partner_id,
                    university_id=university_id,
                    intake_id=intake_id,
                    year_id=year_id,
                    target=target_value
                )


class SetRMUniversityIntakeView(DetailView):
    model = Employee
    template_name = 'users/employee/_rm_set_university_intake.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['years'] = Year.objects.current_to_future()
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        university_id = request.POST.get('university_id')
        intake_id = request.POST.get('intake_id')
        year_id = request.POST.get('year_id')

        if university_id and intake_id and year_id:
            RMUniversityIntake.objects.create(
                rm=self.object,
                university_id=university_id,
                intake_id=intake_id,
                year_id=year_id
            )
            messages.success(request, 'University Intake have been successfully added.')
            return redirect(self.object.get_rm_list_url)


class AssignRegionView(UpdateView):
    model = Employee
    form_class = AssignRegionForm
    template_name = "users/employee/assign_region_form.html"

    # def dispatch(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     if self.object.user.role.name != RoleEnum.REGIONAL_MARKETING_HEAD.value:
    #         messages.warning(request, "Regions can only be assigned to Regional Marketing Heads!")
    #         return redirect(self.object.get_absolute_url)
    #     return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f"Regions successfully assigned.")
        return self.object.get_absolute_url


class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = "users/role/_form.html"

    def get_success_url(self):
        messages.success(self.request, "Role successfully added!")
        return reverse("users:role_list")


class RoleListView(ListView):
    model = Role
    template_name = 'users/role/_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        name = self.request.GET.get('role')
        status = self.request.GET.get('status')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = "users/role/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Role has been successfully updated!')
        return reverse("users:role_list")


class RoleDeleteView(DeleteView):
    model = Role
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Role Deleted Successfully!')
        return reverse("users:role_list")


class ApplicationManagerListView(ListView):
    model = ApplicationManager
    paginate_by = 20
    template_name = "users/employee/application_manager_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employee', 'employee__user', 'employee__assigned_country')
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        status = self.request.GET.get('status')
        mobile_number = self.request.GET.get('mobile_number')

        if name:
            queryset = queryset.filter(employee__user__name__icontains=name)
        if email:
            queryset = queryset.filter(employee__user__email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(employee__mobile_number__icontains=mobile_number)

        if status in ['True', 'False']:
            queryset = queryset.filter(employee__user__is_active=status)

        return queryset


class ApplicationManagerUpdateView(UpdateView):
    model = ApplicationManager
    form_class = ApplicationManagerUpdateForm
    template_name = "users/application_manager/update_application_manager.html"

    def get_success_url(self):
        messages.success(self.request, "Application Manager has been successfully updated!")
        return reverse("users:application_manager_list")
