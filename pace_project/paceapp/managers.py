from django.db import models
from django.utils import timezone


class YearManager(models.Manager):
    def current_year(self):
        current_year = timezone.now().year
        return self.get(intake_year=current_year)

    def past_years(self):
        current_year = timezone.now().year
        return self.filter(intake_year__lt=current_year)

    def future_years(self):
        current_year = timezone.now().year
        return self.filter(intake_year__gt=current_year)

    def current_to_future(self):
        current_year = timezone.now().year
        return self.filter(intake_year__gte=current_year)

    def current_to_past(self):
        current_year = timezone.now().year
        return self.filter(intake_year__lte=current_year)
