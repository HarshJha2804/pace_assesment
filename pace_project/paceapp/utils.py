from datetime import datetime

from crispy_forms.layout import Div
from django.contrib import messages


def calculate_gap_in_years(*, month, year):
    try:
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12.")

        # Validate year (Optional: Define a practical range for year if needed)
        current_year = datetime.now().year
        if not 1 <= year <= current_year:
            raise ValueError(f"Year must be between 1 and {current_year}.")

        current_date = datetime.now()

        # Create a date object for the given month and year
        input_date = datetime(year, month, 1)
        difference_in_days = (current_date - input_date).days
        difference_in_years = difference_in_days // 365

        return difference_in_years

    except ValueError as e:
        print(f"Error: {e}")
        return None


def handle_feedback(request, feedback):
    for error in feedback.get('errors', []):
        messages.error(request, error)

    for success in feedback.get('success', []):
        messages.success(request, success)


def get_student_academic_form_layout():
    layouts = [
        Div('country', css_class='col-md-6'),
        Div('board', css_class='col-md-6'),
        Div('state', css_class='col-md-6'),
        Div('stream', css_class='col-md-6'),
        Div('sub_stream', css_class='col-md-6'),
        Div('passing_month', css_class='col-md-6'),
        Div('passing_year', css_class='col-md-6'),
        Div('tenth_marks', css_class='col-md-6'),
        Div('academic_pathway', css_class='col-md-6'),
    ]
    return layouts


def get_english_test_form_layout():
    layout = [
        Div('english_test_type', css_class='col-md-6'),
        Div('english_overall', css_class='col-md-6'),
        Div('speaking', css_class='col-md-6'),
        Div('writing', css_class='col-md-6'),
        Div('reading', css_class='col-md-6'),
        Div('listening', css_class='col-md-6'),
    ]
    return layout


def validate_assessment_input(course_ids, intake_ids, year_ids):
    return all([course_ids, intake_ids, year_ids])
