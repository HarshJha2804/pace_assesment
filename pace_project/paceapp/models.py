from django.db import models
from model_utils.models import TimeStampedModel
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _
from pace_project.paceapp.managers import YearManager


class Level(TimeStampedModel):
    level = models.CharField(max_length=255)
    streams = models.ManyToManyField("Stream", blank=True)
    boards = models.ManyToManyField("Board", blank=True)

    def __str__(self):
        return self.level

    @property
    def get_absolute_url(self):
        return reverse("paceapp:level_detail", kwargs={"pk": self.pk})


class SubStream(TimeStampedModel):
    sub_stream_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.sub_stream_name


class Stream(TimeStampedModel):
    stream = models.CharField(max_length=255)
    sub_stream = models.ManyToManyField("SubStream", related_name="sub_streams")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.stream

    @property
    def get_absolute_url(self):
        return reverse("paceapp:stream_detail", kwargs={"pk": self.pk})

    @property
    def get_list_url(self):
        return reverse("paceapp:stream_list")


class Intake(TimeStampedModel):
    intake_month = models.CharField(max_length=30)

    def __str__(self):
        return self.intake_month


class Year(TimeStampedModel):
    intake_year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    objects = YearManager()

    class Meta:
        ordering = ['intake_year']

    def __str__(self):
        return str(self.intake_year)


class Country(TimeStampedModel):
    country_name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255, null=True, blank=True)

    country_currency = models.CharField(max_length=255, null=True, blank=True)
    country_currency_symbol = models.CharField(max_length=255, null=True, blank=True)
    commission_frequency = models.CharField(max_length=255, null=True, blank=True)

    country_logo = models.FileField(upload_to='country/logo', null=True, blank=True)
    priority = models.IntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_active_for_student = models.BooleanField(default=True)
    is_active_for_university = models.BooleanField(default=False)

    def __str__(self):
        return self.country_name

    @property
    def get_logo_url(self):
        url = None
        if self.country_logo:
            url = self.country_logo.url
        return url


class Region(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(_("Region Name"), max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["country", "name"]

    def __str__(self):
        return self.name


class State(TimeStampedModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Board(TimeStampedModel):
    country = models.ForeignKey("Country", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['country', 'name']

    def __str__(self):
        return self.name


class Campus(TimeStampedModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class University(TimeStampedModel):
    MEDIUM_CHOICES = [
        ('intakewise', 'Intakewise'),
        ('annually', 'Annually'),
        ('partially', 'Partially'),
    ]
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    alis = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    campus = models.ManyToManyField(Campus)
    application_accepting_from = models.ManyToManyField(Country, related_name='application_accepting_from', blank=True)

    priority = models.IntegerField(null=True, blank=True)
    color_code = models.CharField(max_length=10, null=True, blank=True)
    logo = models.FileField(upload_to='university/logo', null=True, blank=True)
    mini_logo = models.FileField(upload_to="university/mini_logo", null=True, blank=True)

    commission_frequency = models.CharField(max_length=100, choices=MEDIUM_CHOICES, default="intakewise", null=True,
                                            blank=True)

    partially_1 = models.CharField(max_length=100, null=True, blank=True)
    partially_2 = models.CharField(max_length=100, null=True, blank=True)

    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def get_initials(self):
        words = self.name.split()
        if len(words) >= 2:
            first_two_words = words[:2]
            initials = ''.join(word[0].upper() for word in first_two_words)
        else:
            initials = ''.join(word[0].upper() for word in words)
        return initials

    @property
    def get_alis(self):
        return self.alis if self.alis else self.name

    @property
    def get_absolute_url(self):
        return reverse("paceapp:university_detail", kwargs={"pk": self.pk})

    @property
    def application_accept_country_detail(self):
        return reverse("paceapp:application_accept_country_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Universities'
        unique_together = ['country', 'name']

    @property
    def get_logo_url(self):
        if self.logo:
            return self.logo.url
        else:
            return None

    @property
    def get_mini_logo_url(self):
        if self.mini_logo:
            return self.mini_logo.url
        else:
            return None

    @property
    def get_university_list_url(self):
        return reverse("paceapp:university_list")


class UniversityIntake(TimeStampedModel):
    """
    Represents the intake of a university for a specific year and associated campuses.
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    intakes = models.ManyToManyField(Intake)
    campuses = models.ManyToManyField(Campus)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        intake_names = ', '.join([intake.intake_month for intake in self.intakes.all()])
        return f"{self.university.name} - {intake_names}"

    class Meta:
        indexes = [
            models.Index(fields=['university']),
        ]
        ordering = ['university']

    @property
    def get_campuses(self):
        return self.campuses.filter(is_active=True)

    @property
    def get_intakes(self):
        return self.intakes.filter()


class UniversityStateMapping(TimeStampedModel):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    boards = models.ManyToManyField("Board")
    states = models.ManyToManyField("State")
    streams = models.ManyToManyField("Stream")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.university.name


class UniBoardGap(TimeStampedModel):
    """Storing Universities Gaps accept from state wise board."""

    university = models.ForeignKey(University, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    gap = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.university.name


class Course(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    university = models.ForeignKey("University", on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    stream = models.ForeignKey("Stream", on_delete=models.SET_NULL, null=True)
    substream = models.ForeignKey("SubStream", on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=150)
    intake = models.ManyToManyField(Intake)
    campus = models.ManyToManyField(Campus)
    entry_requirement = models.TextField(null=True, blank=True)

    link = models.CharField(max_length=255, null=True, blank=True, help_text=_("course link"))
    tuition_fees = models.CharField(max_length=150, null=True, blank=True)
    scholarship = models.CharField(max_length=150, null=True, blank=True)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    @property
    def get_absolute_url(self):
        return reverse("paceapp:course_detail", kwargs={"pk": self.pk})


class EntryCriteria(TimeStampedModel):
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    country = models.ForeignKey("Country", on_delete=models.CASCADE)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
    tenth_math_marks = models.IntegerField(null=True, blank=True)
    twelfth_math_marks = models.IntegerField(null=True, blank=True)
    twelfth_english_marks = models.IntegerField(null=True, blank=True)
    overall_marks = models.IntegerField(null=True, blank=True)
    best_four_marks = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.course.name


class PGEntryCriteria(TimeStampedModel):
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    country = models.ForeignKey("Country", on_delete=models.CASCADE)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
    twelfth_english_marks = models.IntegerField(null=True, blank=True)
    diploma_overall_marks = models.IntegerField(null=True, blank=True)
    ug_overall_marks = models.IntegerField(null=True, blank=True)
    level_diploma_marks = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.course.name


class EnglishTestType(TimeStampedModel):
    english_test_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.english_test_name


class EnglishTest(TimeStampedModel):
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    country = models.ForeignKey("Country", on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey("EnglishTestType", on_delete=models.SET_NULL, null=True)
    overall = models.CharField(max_length=150)

    speaking = models.CharField(max_length=150)
    listening = models.CharField(max_length=150)
    writing = models.CharField(max_length=150)
    reading = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.course.name


class AssessmentDiscovery(TimeStampedModel):
    """
    Stores assessment discoveries for students by recording the results of discovered assessments.
    """
    student = models.ForeignKey("users.Student", on_delete=models.CASCADE)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey("Course", on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey("Year", on_delete=models.SET_NULL, null=True)
    is_processed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name='assessments_created'
    )

    def __str__(self):
        return self.student.get_full_name

    @property
    def get_apply_application_url(self):
        return reverse("paceapp:apply_application", kwargs={'pk': self.pk})

    @property
    def get_partner_apply_application_url(self):
        return reverse("partner:application_apply", kwargs={'pk': self.pk})

    @property
    def get_notification_url(self):
        return self.student.get_notification_url


class UniversityAgreement(TimeStampedModel):
    university = models.ForeignKey("University", on_delete=models.CASCADE)
    agreement_start_date = models.DateField(null=True, blank=True)
    agreement_end_date = models.DateField(null=True, blank=True)
    upload_agreement = models.FileField(upload_to='university/agreements/', null=True, blank=True)
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True,
                                   related_name="created_agreements")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.university.name
