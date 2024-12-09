from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.cache import cache
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.views.generic.edit import FormMixin, FormView
from django_boost.views.mixins import StaffMemberRequiredMixin, SuperuserRequiredMixin

from pace_project.core.enums import StatusTypeEnum
from pace_project.core.mixins import AMRequiredMixin, ASFRequiredMixin, EmployeeRequiredMixin
from pace_project.core.models.application_models import Application
from pace_project.core.models.generic_models import GenericFollowUp
from pace_project.core.models.core_models import StatusType, PartnerOnBoardingRequest, AssessmentRequest, \
    DailyProgressReport
from pace_project.core.models.target_models import RMTarget
from pace_project.paceapp.enums import LevelEnum, RoleEnum
from pace_project.paceapp.forms import CountryForm, UniversityForm, UniBoardGapForm, UniversityStateMappingForm, \
    UBSSMappingUpdateForm, CourseForm, UpdateCourseForm, EntryCriteriaForm, PGEntryCriteriaForm, EnglishTestForm, \
    BoardForm, StateForm, CampusForm, StreamForm, SubStreamForm, LevelForm, YearForm, PartnerForm, PartnerBranchForm, \
    StudentForm, UGStudentAcademicForm, PGStudentAcademicForm, IntakeForm, PartnerCommunicationForm, RegionForm, \
    UniversityIntakeForm, PartnerOnBoardingRequestForm, DailyProgressReportForm
from pace_project.paceapp.models import Country, University, UniBoardGap, UniversityStateMapping, Course, EntryCriteria, \
    PGEntryCriteria, EnglishTest, Board, State, Campus, Stream, SubStream, Level, Year, AssessmentDiscovery, Intake, \
    Region, UniversityIntake
from pace_project.paceapp.services import is_duplicate_university_board_gap
from pace_project.paceapp.validators import has_application_manager_permission_dashboard
from pace_project.paceapp.validators import has_assessment_permission
from pace_project.users.models import Partner, Student, PartnerBranch, UGStudentAcademic, PGStudentAcademic, \
    PartnerCommunication, PartnerAgreement, Employee
from pace_project.utils.views import BaseListView


class CountryListView(StaffMemberRequiredMixin, ListView):
    model = Country
    paginate_by = 20
    template_name = 'paceapp/course/country_list.html'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('country_name')
        name = self.request.GET.get('name')
        country_code = self.request.GET.get('code')
        status = self.request.GET.get('status')
        if name is not None:
            queryset = queryset.filter(country_name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if country_code:
            queryset = queryset.filter(country_code__icontains=country_code)

        return queryset


class AddCountryView(StaffMemberRequiredMixin, CreateView):
    model = Country
    form_class = CountryForm
    template_name = 'paceapp/country_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Country Added Successfully!')
        return reverse("paceapp:country_list")


class CountryUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Country
    form_class = CountryForm
    template_name = 'paceapp/country_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Country Updated Successfully!')
        return reverse("paceapp:country_list")


class CountryDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Country
    template_name = 'utils/delete_confirmation.html'

    def get_success_url(self):
        messages.success(self.request, 'Country Deleted Successfully!')
        return reverse("paceapp:country_list")


class YearListView(StaffMemberRequiredMixin, ListView):
    model = Year
    template_name = "paceapp/year/_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.GET.get('year')
        status = self.request.GET.get('status')

        if year is not None and year != '':
            queryset = queryset.filter(intake_year__icontains=year)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset


class YearCreateView(StaffMemberRequiredMixin, CreateView):
    model = Year
    form_class = YearForm
    template_name = "paceapp/year/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Year Added Successfully!')
        return reverse("paceapp:year_list")


class YearUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Year
    form_class = YearForm
    template_name = "paceapp/year/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Year has been successfully updated!')
        return reverse("paceapp:year_list")


class YearDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Year
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Year Deleted Successfully!')
        return reverse("paceapp:year_list")


# Level module starts here
class LevelListView(StaffMemberRequiredMixin, ListView):
    model = Level
    paginate_by = 10
    template_name = "paceapp/level/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')

        if name is not None:
            queryset = queryset.filter(level__icontains=name)

        return queryset


class LevelCreateView(StaffMemberRequiredMixin, CreateView):
    model = Level
    form_class = LevelForm
    template_name = "paceapp/level/_form.html"

    def get_success_url(self):
        messages.success(self.request, "Level successfully added!")
        return reverse("paceapp:level_list")


class LevelDetailView(StaffMemberRequiredMixin, DetailView):
    model = Level
    template_name = 'paceapp/level/_detail.html'


class LevelUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Level
    form_class = LevelForm
    template_name = "paceapp/level/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Level has been successfully updated!')
        return reverse("paceapp:level_list")


class LevelDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Level
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Level has been successfully deleted!')
        return reverse("paceapp:level_list")


# Level module ends here

# Stream module starts here
class StreamListView(StaffMemberRequiredMixin, ListView):
    model = Stream
    paginate_by = 10
    template_name = "paceapp/stream/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('level_set').order_by('-created')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        level_id = self.request.GET.get('level')

        if name is not None:
            queryset = queryset.filter(stream__icontains=name)

        if level_id:
            queryset = queryset.filter(level__id=level_id)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Level.objects.all()
        return context


class StreamCreateView(StaffMemberRequiredMixin, CreateView):
    model = Stream
    form_class = StreamForm
    template_name = "paceapp/stream/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Stream Added Successfully!')
        return reverse("paceapp:stream_list")


class StreamDetailView(StaffMemberRequiredMixin, DetailView):
    model = Stream
    template_name = "paceapp/stream/_detail.html"


class StreamUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Stream
    form_class = StreamForm
    template_name = "paceapp/stream/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Stream has been successfully updated!')
        return reverse("paceapp:stream_list")


class StreamDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Stream
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Stream has been successfully deleted!')
        return reverse("paceapp:stream_list")


# Stream module ends here

class SubStreamListView(StaffMemberRequiredMixin, ListView):
    model = SubStream
    paginate_by = 10
    template_name = "paceapp/sub_stream/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        stream = self.request.GET.get('stream')
        level_id = self.request.GET.get('level')

        if name is not None:
            queryset = queryset.filter(sub_stream_name__icontains=name)

        if level_id:
            queryset = queryset.filter(level__id=level_id)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Level.objects.all()
        return context


class SubStreamCreateView(StaffMemberRequiredMixin, CreateView):
    model = SubStream
    form_class = SubStreamForm
    template_name = "paceapp/sub_stream/_form.html"

    def form_valid(self, form):
        res = super().form_valid(form)
        stream = form.cleaned_data.get('stream')
        if stream:
            stream.sub_stream.add(self.object)
        return res

    def get_success_url(self):
        messages.success(self.request, "Sub stream successfully added!")
        return reverse("paceapp:sub_stream_list")


class SubStreamUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = SubStream
    form_class = SubStreamForm
    template_name = "paceapp/sub_stream/_form.html"

    def get_initial(self):
        initials = super().get_initial()
        self.initial_stream = Stream.objects.filter(sub_stream=self.object).first()
        initials['stream'] = self.initial_stream
        return initials

    def form_valid(self, form):
        res = super().form_valid(form)
        stream = form.cleaned_data.get('stream')
        initial_stream = self.initial_stream
        if stream != initial_stream:
            initial_stream.sub_stream.remove(self.object)
            stream.sub_stream.add(self.object)
        return res

    def get_success_url(self):
        messages.success(self.request, 'Sub-Stream successfully updated !')
        return reverse("paceapp:sub_stream_list")


class SubStreamDeleteView(SuperuserRequiredMixin, DeleteView):
    model = SubStream
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Sub-stream successfully deleted !')
        return reverse("paceapp:sub_stream_list")


class RegionCreateView(StaffMemberRequiredMixin, CreateView):
    model = Region
    form_class = RegionForm
    template_name = 'paceapp/region/region_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Region Added Successfully!')
        return reverse("paceapp:region_list")


class RegionListView(StaffMemberRequiredMixin, ListView):
    model = Region
    paginate_by = 10
    template_name = "paceapp/region/region_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        country = self.request.GET.get('country_id')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')

        if country:
            queryset = queryset.filter(country_id=country)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context


class RegionUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Region
    form_class = RegionForm
    template_name = 'paceapp/region/region_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Region has been successfully updated!')
        return reverse("paceapp:region_list")


class RegionDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Region
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Region has been successfully deleted!')
        return reverse("paceapp:region_list")


class StateListView(StaffMemberRequiredMixin, ListView):
    model = State
    paginate_by = 10
    template_name = "paceapp/state/state_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        country = self.request.GET.get('country_id')
        region = self.request.GET.get('region_id')

        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if country:
            queryset = queryset.filter(country_id=country)

        if region:
            queryset = queryset.filter(region_id=region)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        country_id = self.request.GET.get('country_id')
        if country_id:
            context['regions'] = Region.objects.filter(country_id=country_id)
        else:
            context['regions'] = Region.objects.all()
        return context


class StateCreateView(StaffMemberRequiredMixin, CreateView):
    model = State
    form_class = StateForm
    template_name = "paceapp/state/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'State Added Successfully!')
        return reverse("paceapp:state_list")

    def get(self, request, *args, **kwargs):
        country_id = self.request.GET.get('country_id')
        if country_id:
            regions = Region.objects.filter(country_id=country_id).all()
            data = list(regions.values('id', 'name'))
            return JsonResponse(data, safe=False)
        return super().get(request, *args, **kwargs)


class StateUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = State
    form_class = StateForm
    template_name = "paceapp/state/_form.html"

    def get_success_url(self):
        messages.success(self.request, "State has been successfully updated!")
        return reverse("paceapp:state_list")


class StateDeleteView(SuperuserRequiredMixin, DeleteView):
    model = State
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "State has been successfully deleted!")
        return reverse("paceapp:state_list")


class BoardListView(StaffMemberRequiredMixin, ListView):
    model = Board
    paginate_by = 20
    template_name = "paceapp/board/board_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        level_id = self.request.GET.get('level_id')
        country = self.request.GET.get('country_id')

        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if level_id:
            queryset = queryset.filter(level__id=level_id)

        if country:
            queryset = queryset.filter(country_id=country)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['countries'] = Country.objects.all()
        ctx['levels'] = Level.objects.all()
        return ctx


class BoardCreateView(StaffMemberRequiredMixin, CreateView):
    model = Board
    form_class = BoardForm
    template_name = "paceapp/board/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Board Added Successfully!')
        return reverse("paceapp:board_list")


class BoardUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Board
    form_class = BoardForm
    template_name = "paceapp/board/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Board Updated Successfully!')
        return reverse("paceapp:board_list")


class BoardDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Board
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Board has been successfully deleted!")
        return reverse("paceapp:board_list")


class CampusListView(StaffMemberRequiredMixin, ListView):
    model = Campus
    paginate_by = 10
    template_name = "paceapp/campus/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        country = self.request.GET.get('country_id')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)
        if country:
            queryset = queryset.filter(country_id=country)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context


class CampusCreateView(StaffMemberRequiredMixin, CreateView):
    model = Campus
    form_class = CampusForm
    template_name = "paceapp/campus/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Campus Added Successfully!')
        return reverse("paceapp:campus_list")


class CampusUpdateView(UpdateView):
    model = Campus
    form_class = CampusForm
    template_name = "paceapp/campus/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Campus has been successfully updated!')
        return reverse("paceapp:campus_list")


class CampusDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Campus
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Campus has been successfully deleted!')
        return reverse("paceapp:campus_list")


# University Module start
class UniversityListView(StaffMemberRequiredMixin, ListView):
    model = University
    template_name = "paceapp/university_list.html"

    def get_queryset(self):
        CACHE_KEY = "partner_countries_with_universities"
        cached_data = cache.get(CACHE_KEY)
        if cached_data:
            return cached_data

        queryset = University.objects.filter(
            is_active=True, country__is_active_for_university=True
        ).select_related('country').prefetch_related('campus').order_by('country__priority', 'priority')

        countries_with_universities = {}
        for university in queryset:
            country = university.country
            if country not in countries_with_universities:
                countries_with_universities[country] = {
                    "country": country,
                    "universities": []
                }
            countries_with_universities[country]["universities"].append(
                {"id": university.id, "name": university.name, "get_logo_url": university.get_logo_url}
            )

        result = list(countries_with_universities.values())
        cache.set(CACHE_KEY, result, timeout=60 * 60)  # Cache for 1 hour
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        context['campuses'] = Campus.objects.all()
        return context


class UniversityCreateView(StaffMemberRequiredMixin, CreateView):
    model = University
    form_class = UniversityForm
    template_name = 'paceapp/university/university_form.html'

    def get_success_url(self):
        messages.info(self.request, 'Add university state, board and stream mapping!')
        return reverse("paceapp:add_university_state", kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = "Add Project"
        return ctx


class UniversityDetailView(StaffMemberRequiredMixin, DetailView):
    model = University
    template_name = 'paceapp/university/university_detail.html'


class UniversityUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = University
    form_class = UniversityForm
    template_name = 'paceapp/university/university_form.html'

    def get_success_url(self):
        messages.success(self.request, 'University successfully updated!')
        return reverse("paceapp:university_list")


class ApplicationAcceptingFromCountriesDetailView(DetailView):
    model = University
    template_name = 'paceapp/university/application_accepting_from_countries.html'


class AddUniversityGapView(DetailView, FormMixin):
    model = University
    form_class = UniBoardGapForm
    template_name = 'paceapp/university/university_form.html'

    def get_initial(self):
        initials = super().get_initial()
        initials['university'] = self.object
        return initials

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            if is_duplicate_university_board_gap(form=form):
                messages.warning(self.request, 'University gap with this board and state already exists!')
                return self.form_invalid(form=form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.unigap_object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, f"{self.object} university's gap successfully added!")
        return reverse("paceapp:university_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = "Add University Gap"
        return ctx


class UpdateUniBoardGapView(UpdateView):
    model = UniBoardGap
    fields = ['state', 'board', 'gap', 'is_active']
    template_name = 'paceapp/university/university_unigap_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Updated University Gap!')
        return reverse("paceapp:university_detail", kwargs={"pk": self.object.university.pk})


class UniBoardGapDeleteView(DeleteView):
    model = UniBoardGap
    template_name = 'utils/delete_confirmation.html'

    def get_success_url(self):
        messages.success(self.request, 'University gap successfully deleted!')
        return reverse("paceapp:university_detail", kwargs={"pk": self.object.university.pk})


class AddUniversityStateMappingView(DetailView, FormMixin):
    model = University
    form_class = UniversityStateMappingForm
    template_name = 'paceapp/university/university_state_mapping_form.html'

    def get_initial(self):
        initials = super().get_initial()
        initials['university'] = self.object
        return initials

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.unistate_object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Added University Mappings!')
        return reverse("paceapp:university_detail", kwargs={"pk": self.object.pk})


class UBSSMappingUpdateView(UpdateView):
    """University board state stream mapping update view."""
    model = UniversityStateMapping
    form_class = UBSSMappingUpdateForm
    template_name = 'paceapp/university/university_state_mapping_form.html'

    def get_initial(self):
        initials = super().get_initial()
        initials['university'] = self.object.university
        return initials

    def get_success_url(self):
        messages.success(self.request, 'University Mappings successfully updated!')
        return reverse("paceapp:university_detail", kwargs={"pk": self.object.university.pk})


class UniversityStateMappingDeleteView(DeleteView):
    model = UniversityStateMapping
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'University Mapping successfully deleted!')
        return reverse("paceapp:university_detail", kwargs={"pk": self.object.university.pk})


class CourseListView(StaffMemberRequiredMixin, ListView):
    model = Course
    paginate_by = 20
    template_name = 'paceapp/course/course_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        status = self.request.GET.get('status')
        country = self.request.GET.get('country_id')
        university = self.request.GET.get('university')
        level = self.request.GET.get('level')
        stream = self.request.GET.get('stream')
        sub_stream = self.request.GET.get('sub_stream')

        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if country:
            queryset = queryset.filter(country_id=country)

        if university:
            queryset = queryset.filter(university_id=university)

        if level:
            queryset = queryset.filter(level_id=level)

        if stream:
            queryset = queryset.filter(stream_id=stream)

        if sub_stream:
            queryset = queryset.filter(substream__sub_stream_name=sub_stream)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        context['universities'] = University.objects.all()
        context['levels'] = Level.objects.all()
        context['streams'] = Stream.objects.all()
        return context


class AddCourseView(StaffMemberRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "paceapp/course/course_form.html"

    def get_success_url(self):
        messages.success(self.request, "Success! Kindly provide the necessary course requirements.")
        course = self.object

        if course.level.level == LevelEnum.UNDERGRADUATE.value:
            return reverse("paceapp:add_course_requirements", kwargs={"pk": self.object.pk})
        elif course.level.level == LevelEnum.POSTGRADUATE.value:
            return reverse("paceapp:add_pg_course_requirements", kwargs={"pk": self.object.pk})
        else:
            messages.warning(self.request, "We have not setup course requirements yet. for this course level!")
            return reverse("paceapp:course_list")


class CourseDetailView(StaffMemberRequiredMixin, DetailView):
    model = Course
    template_name = "paceapp/course/detail.html"


class CourseUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Course
    form_class = UpdateCourseForm
    template_name = "paceapp/course/course_form.html"

    def get_success_url(self):
        messages.success(self.request, "Course updated successfully!")
        return reverse("paceapp:course_detail", kwargs={"pk": self.object.pk})


class CourseEntryCriteriaUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = EntryCriteria
    form_class = EntryCriteriaForm
    template_name = "paceapp/course/course_requirement_form.html"

    def get_success_url(self):
        messages.success(self.request, "Updated Course entry criteria successfully!")
        return reverse("paceapp:course_detail", kwargs={"pk": self.object.course.pk})


class CourseEntryCriteriaDeleteView(StaffMemberRequiredMixin, UserPassesTestMixin, DeleteView):
    model = EntryCriteria
    template_name = "utils/delete_confirmation.html"

    def test_func(self):
        # Only allow superuser to delete
        return self.request.user.is_superuser

    def get_success_url(self):
        messages.success(self.request, "Deleted Course entry criteria successfully!")
        return reverse("paceapp:course_detail", kwargs={"pk": self.object.course.pk})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Entry criteria deleted successfully.')
        return success_url


class PGEntryCriteriaUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = PGEntryCriteria
    form_class = PGEntryCriteriaForm
    template_name = "paceapp/_form.html"

    def get_success_url(self):
        messages.success(self.request, "Entry criteria successfully updated !")
        return self.object.course.get_absolute_url


class PGEntryCriteriaDeleteView(StaffMemberRequiredMixin, DeleteView):
    model = PGEntryCriteria
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Entry Criteria has been successfully deleted! 🗑️")
        return self.object.course.get_absolute_url


class EnglishTestUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = EnglishTest
    form_class = EnglishTestForm
    template_name = "paceapp/english_test/_form.html"

    def get_success_url(self):
        messages.success(self.request, "English Test successfully updated! ✅")
        return self.object.course.get_absolute_url


class EnglishTestDeleteView(SuperuserRequiredMixin, DeleteView):
    model = EnglishTest
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "English Test has been successfully deleted! 🗑️")
        return self.object.course.get_absolute_url


class PartnerListView(StaffMemberRequiredMixin, BaseListView):
    model = Partner
    paginate_by = 20
    template_name = "paceapp/partner/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created")
        if not self.request.user.is_superuser:
            if self.request.user.role.name == RoleEnum.REGIONAL_MARKETING_HEAD.value:
                queryset = queryset.filter(on_boarded_by=self.request.user)
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        country = self.request.GET.get('country')
        state = self.request.GET.get('state')
        city = self.request.GET.get('city')
        status = self.request.GET.get('status')
        mobile_number = self.request.GET.get('mobile_number')
        email_verified = self.request.GET.get("email_verified")
        agreement_uploaded = self.request.GET.get("agreement_uploaded")

        if name:
            queryset = queryset.filter(company_name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if country:
            queryset = queryset.filter(country_id=country)

        if state:
            queryset = queryset.filter(state_id=state)

        if city:
            queryset = queryset.filter(city__icontains=city)

        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if email_verified in ['True', 'False']:
            partner_emails = queryset.values_list('email', flat=True)
            from allauth.account.models import EmailAddress
            email_addresses = EmailAddress.objects.filter(email__in=partner_emails)
            verified_emails = email_addresses.filter(verified=email_verified).values_list('email', flat=True)
            queryset = queryset.filter(email__in=verified_emails)

        if agreement_uploaded in ["True", "False"]:
            partner_ids_with_agreements = PartnerAgreement.objects.exclude(agreement="").values_list(
                'partner_id', flat=True
            )
            if agreement_uploaded == "False":
                queryset = queryset.exclude(id__in=partner_ids_with_agreements)

            elif agreement_uploaded == "True":
                queryset = queryset.filter(id__in=partner_ids_with_agreements)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        context['states'] = State.objects.all()
        return context


class PartnerCreateView(StaffMemberRequiredMixin, FormView):
    form_class = PartnerForm
    template_name = "paceapp/partner/_form.html"

    def get_success_url(self):
        messages.success(self.request, "Created Partner successfully!")
        return reverse("paceapp:partner_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['States'] = list(State.objects.filter(is_active=True).values('id', 'name', 'country_id'))
        return context

    def form_valid(self, form):
        self.object = form.save(self.request)
        return super().form_valid(form)


class PartnerDetailView(StaffMemberRequiredMixin, FormMixin, DetailView):
    model = Partner
    form_class = PartnerBranchForm
    template_name = "paceapp/partner/_detail.html"

    def get_success_url(self):
        messages.success(self.request, "New branch created successfully!")
        return reverse("paceapp:partner_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['form'] = self.form_class(self.request.POST)
        else:
            ctx['form'] = self.form_class()
        initials = {
            'partner': self.object,
            'branch': self.object.partnerbranch_set.filter(is_head_office=True).first()
        }
        ctx['partner_communication_form'] = PartnerCommunicationForm(initial=initials)
        ctx['follow_ups'] = GenericFollowUp.objects.filter(object_id=self.object.id)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        partner = self.get_object()
        form.instance.partner = partner
        form.save()
        return super().form_valid(form)


class PartnerUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Partner
    form_class = PartnerForm
    template_name = "paceapp/partner/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Partner updated successfully!')
        return reverse("paceapp:partner_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['States'] = list(State.objects.filter(is_active=True).values('id', 'name', 'country_id'))
        return context


class PartnerDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Partner
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Deleted Partner successfully!")
        return reverse("paceapp:partner_list")


# Partner Branch


class PartnerBranchUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = PartnerBranch
    form_class = PartnerBranchForm
    template_name = "paceapp/partner/_branch_form.html"

    def get_success_url(self):
        messages.success(self.request, "Branch detail updated successfully!")
        return reverse("paceapp:partner_detail", kwargs={"pk": self.object.partner.pk})


class PartnerBranchDeleteView(StaffMemberRequiredMixin, DeleteView):
    model = PartnerBranch
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Branch has been successfully deleted!")
        return reverse("paceapp:partner_detail", kwargs={"pk": self.object.partner.pk})


def save_partner_contact_view(request, pk):
    partner = get_object_or_404(Partner, id=pk)
    if request.method == 'POST':
        form = PartnerCommunicationForm(request.POST)
        print('form is valid', form)
        if form.is_valid():
            communication_type = form.cleaned_data.get('communication_type')
            communication_value = form.cleaned_data.get('communication_value')
            country_code = form.cleaned_data.get('country_code')
            branch = form.cleaned_data.get('branch')
            obj = PartnerCommunication.objects.create(
                partner=partner,
                communication_type=communication_type,
                communication_value=communication_value,
                country_code=country_code,
                branch=branch
            )
            obj.save()
            messages.success(request, 'Contact added successfully!!')
        else:
            messages.warning(request, "Invalid Details")
        return redirect(partner.get_absolute_url)


class PartnerContactUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = PartnerCommunication
    form_class = PartnerCommunicationForm
    template_name = 'paceapp/partner/partner_contact_form.html'

    def get_success_url(self):
        messages.success(self.request, "Partner Contact updated successfully!")
        return self.object.partner.get_absolute_url

    def get_initial(self):
        initials = super().get_initial()
        initials['partner'] = self.object.partner
        return initials


class PartnerContactDeleteView(StaffMemberRequiredMixin, DeleteView):
    model = PartnerCommunication
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Partner Contact has been successfully deleted!")
        return self.object.partner.get_absolute_url


class StudentListView(StaffMemberRequiredMixin, ListView):
    model = Student
    paginate_by = 20
    template_name = "paceapp/student/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'partner', 'study_level',
        ).order_by("-created")

        user = self.request.user
        if not user.is_superuser and not user.role.name == RoleEnum.VICE_PRESIDENT.value:
            if user.role.name == RoleEnum.COMPLIANCE_OFFICER.value:
                assigned_country = user.employee.assigned_country
                if assigned_country:
                    queryset = queryset.filter(study_country=assigned_country)
            else:
                queryset = queryset.filter(created_by=user)

        study_country = self.request.GET.get('study_country')
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        partner = self.request.GET.get('partner')
        study_country = self.request.GET.get('study_country')
        study_level = self.request.GET.get('study_level')
        status = self.request.GET.get('status')
        passport_number = self.request.GET.get('passport_number')

        if study_country:
            queryset = queryset.filter(study_country_id=study_country)

        if name:
            queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if email:
            queryset = queryset.filter(email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if partner:
            queryset = queryset.filter(partner_id=partner)
        if study_country:
            queryset = queryset.filter(study_country_id=study_country)

        if study_level:
            queryset = queryset.filter(study_level_id=study_level)

        if passport_number:
            queryset = queryset.filter(passport_number__icontains=passport_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partners'] = Partner.objects.all()
        context['universities'] = University.objects.all()
        context['levels'] = Level.objects.all()
        context['countries'] = Country.objects.filter(is_active_for_university=True)
        return context


class StudentCreateView(StaffMemberRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "paceapp/student/_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Student added successfully!")
        return self.object.get_absolute_url

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return super().form_valid(form)


class StudentDetailView(StaffMemberRequiredMixin, DetailView):
    model = Student
    template_name = "paceapp/student/_detail.html"

    def get_queryset(self):
        return super().get_queryset().select_related(
            'partner', 'study_level', 'study_country', 'assessment_status', 'created_by', 'ugstudentacademic',
            'pgstudentacademic'
        ).prefetch_related('application_set', 'assessmentdiscovery_set')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        academic = None
        if self.object.study_level:
            if self.object.study_level.level == LevelEnum.UNDERGRADUATE.value:
                academic = UGStudentAcademic.objects.filter(student=self.object).first()
            elif self.object.study_level.level == LevelEnum.POSTGRADUATE.value:
                academic = PGStudentAcademic.objects.filter(student=self.object).first()
        ctx['academic'] = academic
        user = self.request.user
        if hasattr(user, 'employee'):
            assigned_universities = user.employee.assigned_universities.filter(is_active=True)
        else:
            assigned_universities = University.objects.filter(is_active=True)

        # Filter applications and assessments by assigned universities
        if self.request.user.is_superuser:
            ctx['applications'] = self.object.get_applications.filter()
            ctx['assessments'] = self.object.get_assessments.filter()
        else:
            ctx['applications'] = self.object.get_applications.filter(course__university__in=assigned_universities)
            ctx['assessments'] = self.object.get_assessments.filter(course__university__in=assigned_universities)

        ctx['universities'] = list(assigned_universities.values('id', 'name'))

        current_year = datetime.now().year
        upcoming_year = current_year + 1
        following_year = current_year + 2
        ctx['years'] = Year.objects.filter(is_active=True,
                                           intake_year__in=[current_year, upcoming_year, following_year])
        ctx['country_specific'] = StatusType.objects.filter(is_active=True)

        if assigned_universities.exists():
            university_id = assigned_universities.first().id
            ctx['course_api_url'] = f"/api/courses/{university_id}/"
            ctx['intake_api_url'] = f"/api/intakes/{university_id}/"
        ctx['not_send_assessment'] = not has_application_manager_permission_dashboard(self.request)
        ctx['not_apply_direct_application'] = False

        if has_assessment_permission(self.request):
            ctx['not_apply_direct_application'] = True
        else:
            if hasattr(user, 'employee') and hasattr(user.employee, 'applicationmanager'):
                app_manager = user.employee.applicationmanager
                if app_manager.is_head and app_manager.will_process_application:
                    ctx['not_apply_direct_application'] = False

        # Filter application managers by assigned universities and student's country
        student_country = self.object.study_country
        ctx['application_manager'] = Employee.objects.filter(
            user__role__name=RoleEnum.APPLICATION_MANAGER.value,
            assigned_universities__in=assigned_universities,
            assigned_country=student_country
        ).distinct()
        return ctx


class StudentUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "paceapp/student/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Student details updated successfully!')
        return reverse("paceapp:student_list")


class StudentDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Student
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Student has been successfully deleted!")
        return reverse("paceapp:student_list")


class AMStudentUpdateView(AMRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "paceapp/student/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Student details updated successfully!')
        return reverse("paceapp:am_student_list")


class AMStudentDeleteView(AMRequiredMixin, DeleteView):
    model = Student
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Student has been successfully deleted!")
        return reverse("paceapp:am_student_list")


class ASFStudentUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "paceapp/student/_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Student details updated successfully!')
        return reverse("paceapp:asf_student_list")


class ASFStudentDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Student
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Student has been successfully deleted!")
        return reverse("paceapp:asf_student_list")


def student_academic_update_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    is_pg = False
    academic_object = None
    if student.study_level.level == LevelEnum.UNDERGRADUATE.value:
        academic_object = get_object_or_404(UGStudentAcademic, student=student)
        form = UGStudentAcademicForm(instance=academic_object)
    elif student.study_level.level == LevelEnum.POSTGRADUATE.value:
        academic_object = get_object_or_404(PGStudentAcademic, student=student)
        form = PGStudentAcademicForm(instance=academic_object)
        is_pg = True
    else:
        form = None
        messages.error(request, 'You have not selected a student level!')

    if request.method == 'POST':
        if is_pg:
            form = PGStudentAcademicForm(request.POST, instance=academic_object)
        else:
            form = UGStudentAcademicForm(request.POST, instance=academic_object)

        if form.is_valid():
            form.save()
            messages.success(request, "Academic details updated successfully!")
            return redirect(student.get_absolute_url)

    context = {
        "form": form,
        'student': student,
    }
    return render(request, 'paceapp/student/academics_form.html', context)


class AssessmentDiscoveryListView(SuperuserRequiredMixin, ListView):
    model = AssessmentDiscovery
    paginate_by = 20
    template_name = "paceapp/assessment_discovery/_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created")
        name = self.request.GET.get('name')
        partner = self.request.GET.get('partner')
        status = self.request.GET.get('status')
        level = self.request.GET.get('level')
        mobile_number = self.request.GET.get('mobile_number')

        if name:
            queryset = queryset.filter(
                Q(student__first_name__icontains=name) |
                Q(student__last_name__icontains=name)
            )

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if partner:
            queryset = queryset.filter(student__partner_id=partner)

        if level:
            queryset = queryset.filter(student__study_level_id=level)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Level.objects.all()
        context['partners'] = Partner.objects.all()
        return context


class IntakeCreateView(StaffMemberRequiredMixin, CreateView):
    model = Intake
    form_class = IntakeForm
    template_name = "paceapp/intake/form.html"

    def get_success_url(self):
        messages.success(self.request, 'Intake Added Successfully!')
        return reverse("paceapp:intake_list")


class IntakeListView(StaffMemberRequiredMixin, ListView):
    model = Intake
    template_name = "paceapp/intake/list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('intake')

        if name:
            queryset = queryset.filter(intake_month__icontains=name)

        return queryset


class IntakeUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = Intake
    form_class = IntakeForm
    template_name = "paceapp/intake/form.html"

    def get_success_url(self):
        messages.success(self.request, 'Intake has been successfully updated!')
        return reverse("paceapp:intake_list")


class IntakeDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Intake
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'Intake Deleted Successfully!')
        return reverse("paceapp:intake_list")


class UniversityIntakeCreateView(StaffMemberRequiredMixin, CreateView):
    model = UniversityIntake
    form_class = UniversityIntakeForm
    template_name = 'paceapp/university_intake/university_intake_form.html'

    def get_success_url(self):
        messages.success(self.request, 'University Intake Added Successfully!')
        return reverse("paceapp:university_intake_list")


class UniversityIntakeListView(StaffMemberRequiredMixin, ListView):
    model = UniversityIntake
    template_name = "paceapp/university_intake/university_intake_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        university = self.request.GET.get('university_id')
        intakes = self.request.GET.get('intakes_id')
        campuses = self.request.GET.get('campuses_id')
        status = self.request.GET.get('status')

        if university:
            queryset = queryset.filter(university_id=university)

        if intakes:
            queryset = queryset.filter(intakes__id=intakes)

        if campuses:
            queryset = queryset.filter(campuses__id=campuses)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['universities'] = University.objects.all()
        context['intakes'] = Intake.objects.filter()
        context['campuses'] = Campus.objects.filter(is_active=True)

        return context


class UniversityIntakeUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = UniversityIntake
    form_class = UniversityIntakeForm
    template_name = "paceapp/university_intake/university_intake_form.html"

    def get_success_url(self):
        messages.success(self.request, 'University Intake has been successfully updated!')
        return reverse("paceapp:university_intake_list")


class UniversityIntakeDeleteView(SuperuserRequiredMixin, DeleteView):
    model = UniversityIntake
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, 'University Intake Deleted Successfully!')
        return reverse("paceapp:university_intake_list")


class AssessmentListView(EmployeeRequiredMixin, ListView):
    model = AssessmentRequest
    paginate_by = 20
    template_name = 'paceapp/dashboard/assessment_officer_dashboard/total_assessment_list.html'

    def get_queryset(self):
        assigned_universities = self.employee.assigned_universities.all()

        # Base queryset for assessments tied to assigned universities
        queryset = super().get_queryset().filter(university__in=assigned_universities)

        # Retrieve received students in a single query, flattening the results
        received_students = AssessmentDiscovery.objects.filter(
            course__university__in=assigned_universities
        ).values_list("student", flat=True)

        # Filter logic based on 'filter' parameter in the GET request
        filter_type = self.request.GET.get('filter')

        filters = {
            'total': {},  # Default filter: all for assigned universities
            'sent': {'student__in': received_students, 'is_active': True},
            'rejected': {'is_active': False}
        }

        if filter_type in filters:
            queryset = queryset.filter(**filters[filter_type])

        return queryset


class ActiveCountryListView(ListView):
    model = Country
    paginate_by = 20
    template_name = 'paceapp/dashboard/data_management_officer_dashboard/active_country_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.GET.get('filter')
        if filter_type == 'active-country-for-university':
            queryset = queryset.filter(is_active_for_university=True)
        elif filter_type == 'active-country-for-student':
            queryset = queryset.filter(is_active_for_student=True)
        return queryset


class ActiveCourseListView(StaffMemberRequiredMixin, ListView):
    model = Course
    paginate_by = 20
    template_name = 'paceapp/dashboard/data_management_officer_dashboard/total_courses.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.request.GET.get('filter')
        if filter_type == 'active-courses':
            queryset = queryset.filter(is_active=True)
        elif filter_type == 'inactive-courses':
            queryset = queryset.filter(is_active=False)
        return queryset


class AMStudentListView(AMRequiredMixin, ListView):
    model = Student
    paginate_by = 20
    template_name = "paceapp/student/am_student_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().select_related('partner', 'study_level').order_by("-created")

        if self.employee.applicationmanager:
            queryset = queryset.filter(study_country=self.employee.assigned_country)

        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        partner = self.request.GET.get('partner')
        study_country = self.request.GET.get('study_country')
        study_level = self.request.GET.get('study_level')
        status = self.request.GET.get('status')
        passport_number = self.request.GET.get('passport_number')

        if name:
            queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if email:
            queryset = queryset.filter(email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if partner:
            queryset = queryset.filter(partner_id=partner)

        if study_country:
            queryset = queryset.filter(study_country_id=study_country)

        if study_level:
            queryset = queryset.filter(study_level_id=study_level)

        if passport_number:
            queryset = queryset.filter(passport_number__icontains=passport_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partners'] = Partner.objects.all()
        context['universities'] = University.objects.all()
        context['levels'] = Level.objects.all()
        context['countries'] = Country.objects.filter(is_active_for_university=True)
        return context


class AssessmentOfficerStudentListView(ASFRequiredMixin, ListView):
    model = Student
    paginate_by = 20
    template_name = "paceapp/student/asf_student_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().select_related('partner', 'study_level').order_by("-created")

        if RoleEnum.ASSESSMENT_OFFICER:
            queryset = queryset.filter(study_country=self.employee.assigned_country)

        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        mobile_number = self.request.GET.get('mobile_number')
        partner = self.request.GET.get('partner')
        study_country = self.request.GET.get('study_country')
        study_level = self.request.GET.get('study_level')
        status = self.request.GET.get('status')
        passport_number = self.request.GET.get('passport_number')

        if name:
            queryset = queryset.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if email:
            queryset = queryset.filter(email__icontains=email)
        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if partner:
            queryset = queryset.filter(partner_id=partner)
        if study_country:
            queryset = queryset.filter(study_country_id=study_country)

        if study_level:
            queryset = queryset.filter(study_level_id=study_level)

        if passport_number:
            queryset = queryset.filter(passport_number__icontains=passport_number)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partners'] = Partner.objects.all()
        context['universities'] = University.objects.all()
        context['levels'] = Level.objects.all()
        context['countries'] = Country.objects.filter(is_active_for_university=True)
        return context


class OnboardingPartnerCreateView(CreateView):
    model = PartnerOnBoardingRequest
    form_class = PartnerOnBoardingRequestForm
    template_name = "paceapp/partner/partner_onboarding_form.html"

    def get_success_url(self):
        messages.success(self.request, "Created Partner successfully!")
        return reverse("paceapp:onboarded_partner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['States'] = list(State.objects.filter(is_active=True).values('id', 'name', 'country_id'))
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.on_boarded_by = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class OnboardingPartnerListView(ListView):
    model = PartnerOnBoardingRequest
    template_name = "paceapp/partner/onboarding_partner_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created")
        if not self.request.user.is_superuser:
            if self.request.user.role.name == RoleEnum.REGIONAL_MARKETING_HEAD.value:
                queryset = queryset.filter(on_boarded_by=self.request.user)
        name = self.request.GET.get('name')
        email = self.request.GET.get('email')
        country = self.request.GET.get('country')
        status = self.request.GET.get('status')
        mobile_number = self.request.GET.get('mobile_number')
        email_verified = self.request.GET.get("email_verified")
        agreement_uploaded = self.request.GET.get("agreement_uploaded")

        if name:
            queryset = queryset.filter(company_name__icontains=name)

        if status in ['True', 'False']:
            queryset = queryset.filter(is_active=status)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if country:
            queryset = queryset.filter(country_id=country)

        if mobile_number:
            queryset = queryset.filter(mobile_number__icontains=mobile_number)

        if email_verified in ['True', 'False']:
            partner_emails = queryset.values_list('email', flat=True)
            from allauth.account.models import EmailAddress
            email_addresses = EmailAddress.objects.filter(email__in=partner_emails)
            verified_emails = email_addresses.filter(verified=email_verified).values_list('email', flat=True)
            queryset = queryset.filter(email__in=verified_emails)

        if agreement_uploaded in ["True", "False"]:
            partner_ids_with_agreements = PartnerAgreement.objects.exclude(agreement="").values_list(
                'partner_id', flat=True
            )
            if agreement_uploaded == "False":
                queryset = queryset.exclude(id__in=partner_ids_with_agreements)

            elif agreement_uploaded == "True":
                queryset = queryset.filter(id__in=partner_ids_with_agreements)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context


class OnBoardedPartnerUpdateView(StaffMemberRequiredMixin, UpdateView):
    model = PartnerOnBoardingRequest
    form_class = PartnerOnBoardingRequestForm
    template_name = "paceapp/partner/partner_onboarding_form.html"

    def get_success_url(self):
        messages.success(self.request, 'Partner updated successfully!')
        # return reverse("paceapp:onboarded_partner")
        return reverse("paceapp:onboarded_partner_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['States'] = list(State.objects.filter(is_active=True).values('id', 'name', 'country_id'))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class OnboardingPartnerDeleteView(SuperuserRequiredMixin, DeleteView):
    model = PartnerOnBoardingRequest
    template_name = "utils/delete_confirmation.html"

    def get_success_url(self):
        messages.success(self.request, "Deleted Partner successfully!")
        return reverse("paceapp:onboarded_partner")


class OnboardingPartnerDetailView(StaffMemberRequiredMixin, DetailView):
    model = PartnerOnBoardingRequest
    form_class = PartnerOnBoardingRequestForm
    template_name = "partner/partner_onboarding_detail.html"


class PartnerAccountManagerApplicationListView(ListView):
    model = Application
    template_name = 'dashboard/partner_account_manager/application_list.html'

    def get_queryset(self):
        user_regions = self.request.user.employee.assigned_regions.all()

        queryset = super().get_queryset().filter(student__partner__state__region__in=user_regions).order_by('-created')
        filters = {
            'student__first_name__icontains': self.request.GET.get('student'),
            'student__passport_number__icontains': self.request.GET.get('passport_number'),
            'student__date_of_birth__icontains': self.request.GET.get('date_of_birth'),
            'course__country__id': self.request.GET.get('country'),
            'course__university__id': self.request.GET.get('university'),
            'student__partner_id': self.request.GET.get('agent_name'),
            'student__partner__city__icontains': self.request.GET.get('agent_city'),
            'course__level__icontains': self.request.GET.get('level'),
            'course__name__icontains': self.request.GET.get('course'),
            'current_status_id': self.request.GET.get('current_status'),
            'intake_id': self.request.GET.get('intake'),
            'year_id': self.request.GET.get('year'),
        }

        filters = {k: v for k, v in filters.items() if v}

        if filters:
            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        # assigned_country = self.assigned_country
        # country_status = CountrySpecificStatus.objects.filter(country=assigned_country, is_active=True)
        rms_filtered = []
        seen_combinations = set()
        rms = RMTarget.objects.filter(
            university_id__in=queryset.values_list('course__university', flat=True).distinct(),
            intake_id__in=queryset.values_list('intake', flat=True).distinct(),
            year_id__in=queryset.values_list('year', flat=True).distinct(),
            is_active=True
        ).select_related('rm', 'rm__user')

        for rm in rms:
            key = (rm.university_id, rm.intake_id, rm.year_id, rm.rm.user.name)
            if key not in seen_combinations:
                seen_combinations.add(key)
                rms_filtered.append(rm)

        context['rms'] = rms_filtered
        context['university'] = University.objects.all()
        context['countries'] = Country.objects.filter()
        context['partners'] = Partner.objects.all()
        context['intakes'] = Intake.objects.all()
        context['years'] = Year.objects.all()
        context['statuses'] = StatusType.objects.filter()
        return context


class DailyProgressReportCreateView(CreateView):
    model = DailyProgressReport
    form_class = DailyProgressReportForm
    template_name = 'dashboard/regional_marketing_head/daily_progress_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['created_by'] = self.request.user
        return initial

    def get_success_url(self):
        messages.success(self.request, 'Daily progress report successfully created')
        return reverse("paceapp:daily_report_list")


class DailyProgressReportListView(ListView):
    model = DailyProgressReport
    template_name = 'dashboard/regional_marketing_head/daily_progress_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(created_by=self.request.user).order_by('created')
        if self.request.user.is_superuser:
            queryset = super().get_queryset().all()

        date = self.request.GET.get('scheduled_date')
        partner = self.request.GET.get('assigned_to')

        if date:
            queryset = queryset.filter(activity_date=date)
        if partner:
            queryset = queryset.filter(task_partner__icontains=partner)

        return queryset


class DailyReportUpdateView(UpdateView):
    model = DailyProgressReport
    form_class = DailyProgressReportForm
    template_name = 'dashboard/regional_marketing_head/daily_progress_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Daily progress report successfully updated')
        return reverse("paceapp:daily_report_list")
