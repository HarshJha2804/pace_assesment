import csv
from pace_project.paceapp.models import Country, University, Level, Stream, SubStream, Intake, Campus, Course
from typing import List, Optional, Dict
from django.db.models import QuerySet


def fetch_country(*, name: str) -> Optional[Country]:
    return Country.objects.filter(country_name__iexact=name).first()


def fetch_university(*, name: str, country: Country) -> Optional[University]:
    return University.objects.filter(name__iexact=name, country=country).first()


def fetch_level(*, name: str) -> Optional[Level]:
    return Level.objects.filter(level__iexact=name).first()


def fetch_stream(*, name: str) -> Optional[Stream]:
    return Stream.objects.filter(stream__iexact=name, is_active=True).first()


def fetch_substream(*, name: str) -> Optional[SubStream]:
    return SubStream.objects.filter(sub_stream_name__iexact=name, is_active=True).first()


def fetch_campuses(*, campus_names: List[str], country: Country) -> QuerySet[Campus]:
    """Fetch campuses by names and country, case-insensitive."""
    campuses = Campus.objects.none()
    for name in campus_names:
        campus = Campus.objects.filter(name__iexact=name.strip(), country=country)
        if campus.exists():
            campuses = campuses | campus
    return campuses.distinct()


def fetch_intakes(*, intake_names: List[str]) -> QuerySet[Intake]:
    """Fetch intakes by names, case-insensitive."""
    intakes = Intake.objects.none()
    for name in intake_names:
        intake = Intake.objects.filter(intake_month__iexact=name.strip())
        if intake.exists():
            intakes = intakes | intake
    return intakes.distinct()


def is_course_existing(*, name: str, university: University) -> bool:
    return Course.objects.filter(name__iexact=name, university=university).exists()


def create_course(*, course_data: Dict) -> Optional[Course]:
    """Create a new course using provided data."""
    try:
        return Course.objects.create(**course_data)
    except Exception as e:
        print(f"Error creating course: {e}")
        return None


def load_courses_from_csv():
    """Load and save courses from a CSV file into the database."""
    csv_file_path = "F:\pace\dump\course-data.csv"

    with open(csv_file_path, mode='r') as file:
        course_reader = csv.DictReader(file)
        added_count = 0
        existing_count = 0

        for course_data in course_reader:
            # Fetch core data
            country_name = course_data.get('country', '').strip()
            university_name = course_data.get('university', '').strip()
            course_name = course_data.get("name", '').strip()

            if not (country_name and university_name and course_name):
                continue  # Skip if essential data is missing

            country = fetch_country(name=country_name)
            if not country:
                print(f"Country '{country_name}' not found. Skipping.")
                continue

            university = fetch_university(name=university_name, country=country)
            if not university:
                print(f"University '{university_name}' not found in '{country_name}'. Skipping.")
                continue

            if is_course_existing(name=course_name, university=university):
                existing_count += 1
                print(f"Course '{course_name}' already exists for '{university_name}'. Skipping.")
                continue

            # Optional Data Retrieval
            level = fetch_level(name=course_data.get("level", '').strip())
            stream = fetch_stream(name=course_data.get("stream", '').strip())
            substream = fetch_substream(name=course_data.get("substream", '').strip())

            campus_names = [name.strip() for name in course_data.get("campus", '').split(",") if name.strip()]
            campuses = fetch_campuses(campus_names=campus_names, country=country)

            intake_names = [name.strip() for name in course_data.get("intake", '').split(",") if name.strip()]
            intakes = fetch_intakes(intake_names=intake_names)

            # Prepare Course Data
            new_course_data = {
                "country": country,
                "university": university,
                "level": level,
                "stream": stream,
                "substream": substream,
                "name": course_name,
                "link": course_data.get("link", '').strip(),
                "tuition_fees": course_data.get("tuition_fees", '').strip(),
                "scholarship": course_data.get("scholarship", '').strip(),
                "entry_requirement": course_data.get("entry_requirement", '').strip(),
                "is_active": course_data.get("is_active", '').strip().lower() == "true",
            }

            # Create Course and Add Related Data
            course_obj = create_course(course_data=new_course_data)
            if course_obj:
                course_obj.campus.set(campuses)
                course_obj.intake.set(intakes)
                added_count += 1
                print(f"{added_count}. Added Course: {course_name}")

    print(f"\nSummary: {added_count} courses added, {existing_count} courses skipped (already exist).")
