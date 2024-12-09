from django.shortcuts import get_object_or_404

from pace_project.paceapp.models import Year, University, UniversityStateMapping, UniBoardGap, Course, EntryCriteria, \
    EnglishTest, PGEntryCriteria
from pace_project.paceapp.utils import calculate_gap_in_years
from pace_project.users.models import UGStudentAcademic, PGStudentAcademic


def filter_universities(*, form_data):
    country_id = form_data.get("country_id")
    board_id = form_data.get("board_id")
    state_id = form_data.get("state_id")
    stream_id = form_data.get("stream_id")

    passing_month = form_data.get("passing_month")
    year_id = form_data.get("year_id")

    year = get_object_or_404(Year, pk=year_id)
    student_gap = calculate_gap_in_years(month=int(passing_month), year=int(year.intake_year))
    print("Student Gap", student_gap)

    # University Level Filters
    # Step 1: Filter universities accepting the student's country
    universities = University.objects.filter(
        application_accepting_from__id=country_id,
        is_active=True
    )
    print("Universities after country filter: ", universities)

    # Step 2: Filter universities by board, state, and stream
    university_state_mappings = UniversityStateMapping.objects.filter(
        university__in=universities,
        boards__id=board_id,
        states__id=state_id,
        streams__id=stream_id,
        is_active=True
    ).distinct('university')
    valid_universities = university_state_mappings.values_list('university', flat=True)
    print("Universities after board, state, and stream filter: ", valid_universities)

    # Step 3: Filter universities by board, state, and student gap
    university_board_gaps = UniBoardGap.objects.filter(
        university__in=valid_universities,
        board_id=board_id,
        state_id=state_id,
        gap__gte=student_gap,
        is_active=True
    ).distinct('university')
    valid_universities = university_board_gaps.values_list('university', flat=True)
    filtered_universities = University.objects.filter(id__in=valid_universities)
    print("Universities after board, state, Gap filter: ", valid_universities)

    return filtered_universities


def filter_courses(*, valid_universities, form_data):
    """
    Filter courses based on universities and course requirements.

    Args:
        - valid_universities: List of filtered university IDs that match all the requirements.
        - form_data: Dictionary containing course requirements.
    """
    # Extracting form data
    country_id = form_data.get("country_id")
    level_id = form_data.get("level_id")
    board_id = form_data.get("board_id")

    tenth_marks = form_data.get("tenth_marks")
    academic_pathway = form_data.get("academic_pathway")
    diploma_overall = form_data.get("diploma_overall")

    twelfth_overall = form_data.get("twelfth_overall")
    twelfth_math_marks = form_data.get("twelfth_math_marks")
    twelfth_eng_marks = form_data.get("twelfth_eng_marks")
    best_four_marks = form_data.get("best_four_marks")

    english_test_id = form_data.get("english_test_id")
    eng_test_overall = form_data.get("eng_test_overall")

    speaking = form_data.get("speaking")
    writing = form_data.get("writing")
    reading = form_data.get("reading")
    listening = form_data.get("listening")

    # Step 1: Filter courses of the filtered universities
    # TODO: Add condition in UG & PG to check level_id passed or not, If not then return message that level not found.
    courses = Course.objects.filter(
        university_id__in=valid_universities,
        level_id=level_id,
        is_active=True
    )
    print("Courses after university filter: ", courses)

    # Step 2: Initialize entry criteria filters
    criteria_filters = {
        'course__in': courses,
        'country_id': country_id,
        'board_id': board_id,
        'is_active': True
    }
    if tenth_marks:
        criteria_filters.update({
            'tenth_math_marks__lte': tenth_marks
        })

    # Step 3: Update criteria filters based on academic pathway
    if academic_pathway == "intermediate":
        criteria_filters.update({
            'twelfth_math_marks__lte': twelfth_math_marks,
            'twelfth_english_marks__lte': twelfth_eng_marks,
            'overall_marks__lte': twelfth_overall,
            'best_four_marks__lte': best_four_marks,
        })

    elif academic_pathway == "diploma":
        criteria_filters.update({
            'overall_marks__lte': diploma_overall
        })

    # Step 4: Filter entry criteria and get course IDs
    if academic_pathway in ["intermediate", "diploma"]:
        entry_criteria = EntryCriteria.objects.filter(**criteria_filters).values_list('course', flat=True)
    else:
        entry_criteria = []

    print("Courses after entry criteria filter: ", entry_criteria)

    # Step 5: Filter courses by English test criteria
    english_tests = EnglishTest.objects.filter(
        course__in=entry_criteria,
        type_id=english_test_id,
        overall__lte=eng_test_overall,
        speaking__lte=speaking,
        writing__lte=writing,
        reading__lte=reading,
        listening__lte=listening,
        is_active=True
    ).values_list('course', flat=True)
    print("Courses after English test filter: ", english_tests)

    return Course.objects.filter(id__in=english_tests)


def filter_pg_courses(*, valid_universities, form_data):
    """
        Filter Postgraduate (PG) courses based on universities and course requirements.

        Args:
            - valid_universities: List of filtered university IDs that match all the requirements.
            - form_data: Dictionary containing course requirements.
    """
    # Extracting form data
    country_id = form_data.get("country_id")
    level_id = form_data.get("level_id")
    board_id = form_data.get("board_id")

    academic_pathway = form_data.get("academic_pathway")
    diploma_overall = form_data.get("diploma_overall")

    twelfth_eng_marks = form_data.get("twelfth_eng_marks")
    ug_overall = form_data.get("ug_overall")
    level_diploma = form_data.get("level_diploma")

    english_test_id = form_data.get("english_test_id")
    eng_test_overall = form_data.get("eng_test_overall")

    speaking = form_data.get("speaking")
    writing = form_data.get("writing")
    reading = form_data.get("reading")
    listening = form_data.get("listening")

    # Step 1: Filter courses of the filtered universities
    courses = Course.objects.filter(
        university_id__in=valid_universities,
        level_id=level_id,
        is_active=True
    )

    print("PG Courses after university filter: ", courses)

    # Step 2: Initialize entry criteria filters
    criteria_filters = {
        'course__in': courses,
        'country_id': country_id,
        'board_id': board_id,
        'is_active': True
    }

    # Step 3: Update criteria filters based on academic pathway
    if academic_pathway == "intermediate_ug":
        criteria_filters.update({
            'twelfth_english_marks__lte': twelfth_eng_marks,
            'ug_overall_marks__lte': ug_overall,
        })

    elif academic_pathway == "diploma_ug":
        criteria_filters.update({
            'diploma_overall_marks__lte': diploma_overall,
            'ug_overall_marks__lte': ug_overall
        })
    elif academic_pathway == "level_diploma":
        criteria_filters.update({
            'level_diploma_marks__lte': level_diploma
        })

    # Step 4: Filter entry criteria and get course IDs
    if academic_pathway in ["intermediate_ug", "diploma_ug", "level_diploma"]:
        entry_criteria = PGEntryCriteria.objects.filter(**criteria_filters).values_list('course', flat=True)
    else:
        entry_criteria = []
    print("PG Courses after entry criteria filter: ", entry_criteria)

    # Step 5: Filter courses by English test criteria
    english_tests = EnglishTest.objects.filter(
        course__in=entry_criteria,
        type_id=english_test_id,
        overall__lte=eng_test_overall,
        speaking__lte=speaking,
        writing__lte=writing,
        reading__lte=reading,
        listening__lte=listening,
        is_active=True
    ).values_list('course', flat=True)
    print("Courses after English test filter: ", english_tests)

    return Course.objects.filter(id__in=english_tests)


"""
Filter courses of stored academic details:
-----------------------------------------
"""


def filter_universities_by_student(*, student_academic):
    country_id = student_academic.country_id
    board_id = student_academic.board_id
    state_id = student_academic.state_id
    stream_id = student_academic.stream_id

    passing_month = student_academic.passing_month
    year_id = student_academic.passing_year_id

    year = get_object_or_404(Year, pk=year_id)
    student_gap = calculate_gap_in_years(month=int(passing_month), year=int(year.intake_year))
    print("Student Gap", student_gap)

    # University Level Filters
    # Step 1: Filter universities accepting the student's country
    universities = University.objects.filter(
        application_accepting_from__id=country_id,
        is_active=True
    )
    print("Universities after country filter: ", universities)

    # Step 2: Filter universities by board, state, and stream
    university_state_mappings = UniversityStateMapping.objects.filter(
        university__in=universities,
        boards__id=board_id,
        states__id=state_id,
        streams__id=stream_id,
        is_active=True
    ).distinct('university')
    valid_universities = university_state_mappings.values_list('university', flat=True)
    print("Universities after board, state, and stream filter: ", valid_universities)

    # Step 3: Filter universities by board, state, and student gap
    university_board_gaps = UniBoardGap.objects.filter(
        university__in=valid_universities,
        board_id=board_id,
        state_id=state_id,
        gap__gte=student_gap,
        is_active=True
    ).distinct('university')
    valid_universities = university_board_gaps.values_list('university', flat=True)
    filtered_universities = University.objects.filter(id__in=valid_universities)
    print("Universities after board, state, Gap filter: ", valid_universities)

    return filtered_universities


def filter_ug_courses_by_student(*, valid_universities, student_academic: UGStudentAcademic):
    """
    Filter courses based on universities and course requirements.

    Args:
        - valid_universities: List of filtered university IDs that match all the requirements.
        - form_data: Dictionary containing course requirements.
    """
    # Extracting form data
    country_id = student_academic.country_id
    level_id = student_academic.student.study_level_id
    board_id = student_academic.board_id

    tenth_marks = student_academic.tenth_marks
    academic_pathway = student_academic.academic_pathway
    diploma_overall = student_academic.overall_marks

    twelfth_overall = student_academic.overall_marks
    twelfth_math_marks = student_academic.twelfth_math_marks
    twelfth_eng_marks = student_academic.twelfth_english_marks
    best_four_marks = student_academic.twelfth_best_four_marks

    english_test_id = student_academic.english_test_type_id
    eng_test_overall = student_academic.english_overall

    speaking = student_academic.speaking
    writing = student_academic.writing
    reading = student_academic.reading
    listening = student_academic.listening

    # Step 1: Filter courses of the filtered universities
    # TODO: Add condition in UG & PG to check level_id passed or not, If not then return message that level not found.
    courses = Course.objects.filter(
        university_id__in=valid_universities,
        level_id=level_id,
        is_active=True
    )
    print("Courses after university filter: ", courses)

    # Step 2: Initialize entry criteria filters
    criteria_filters = {
        'course__in': courses,
        'country_id': country_id,
        'board_id': board_id,
        'is_active': True
    }
    if tenth_marks:
        criteria_filters.update({
            'tenth_math_marks__lte': tenth_marks
        })

    # Step 3: Update criteria filters based on academic pathway
    if academic_pathway == "intermediate":
        criteria_filters.update({
            'twelfth_math_marks__lte': twelfth_math_marks,
            'twelfth_english_marks__lte': twelfth_eng_marks,
            'overall_marks__lte': twelfth_overall,
            'best_four_marks__lte': best_four_marks,
        })

    elif academic_pathway == "diploma":
        criteria_filters.update({
            'overall_marks__lte': diploma_overall
        })

    # Step 4: Filter entry criteria and get course IDs
    if academic_pathway in ["intermediate", "diploma"]:
        entry_criteria = EntryCriteria.objects.filter(**criteria_filters).values_list('course', flat=True)
    else:
        entry_criteria = []

    print("Courses after entry criteria filter: ", entry_criteria)

    # Step 5: Filter courses by English test criteria
    english_tests = EnglishTest.objects.filter(
        course__in=entry_criteria,
        type_id=english_test_id,
        overall__lte=eng_test_overall,
        speaking__lte=speaking,
        writing__lte=writing,
        reading__lte=reading,
        listening__lte=listening,
        is_active=True
    ).values_list('course', flat=True)
    print("Courses after English test filter: ", english_tests)

    return Course.objects.filter(id__in=english_tests)


def filter_pg_courses_by_student(*, valid_universities, student_academic: PGStudentAcademic):
    """
        Filter Postgraduate (PG) courses based on universities and course requirements.

        Args:
            - valid_universities: List of filtered university IDs that match all the requirements.
            - form_data: Dictionary containing course requirements.
    """
    # Extracting form data
    country_id = student_academic.country_id
    level_id = student_academic.student.study_level_id
    board_id = student_academic.board_id

    academic_pathway = student_academic.academic_pathway
    diploma_overall = student_academic.diploma_overall_marks

    twelfth_eng_marks = student_academic.twelfth_english_marks
    ug_overall = student_academic.ug_overall_marks
    level_diploma = student_academic.level_diploma_marks

    english_test_id = student_academic.english_test_type_id
    eng_test_overall = student_academic.english_overall

    speaking = student_academic.speaking
    writing = student_academic.writing
    reading = student_academic.reading
    listening = student_academic.listening

    # Step 1: Filter courses of the filtered universities
    courses = Course.objects.filter(
        university_id__in=valid_universities,
        level_id=level_id,
        is_active=True
    )

    print("PG Courses after university filter: ", courses)

    # Step 2: Initialize entry criteria filters
    criteria_filters = {
        'course__in': courses,
        'country_id': country_id,
        'board_id': board_id,
        'is_active': True
    }

    # Step 3: Update criteria filters based on academic pathway
    if academic_pathway == "intermediate_ug":
        criteria_filters.update({
            'twelfth_english_marks__lte': twelfth_eng_marks,
            'ug_overall_marks__lte': ug_overall,
        })

    elif academic_pathway == "diploma_ug":
        criteria_filters.update({
            'diploma_overall_marks__lte': diploma_overall,
            'ug_overall_marks__lte': ug_overall
        })
    elif academic_pathway == "level_diploma":
        criteria_filters.update({
            'level_diploma_marks__lte': level_diploma
        })

    # Step 4: Filter entry criteria and get course IDs
    if academic_pathway in ["intermediate_ug", "diploma_ug", "level_diploma"]:
        entry_criteria = PGEntryCriteria.objects.filter(**criteria_filters).values_list('course', flat=True)
    else:
        entry_criteria = []
    print("PG Courses after entry criteria filter: ", entry_criteria)

    # Step 5: Filter courses by English test criteria
    english_tests = EnglishTest.objects.filter(
        course__in=entry_criteria,
        type_id=english_test_id,
        overall__lte=eng_test_overall,
        speaking__lte=speaking,
        writing__lte=writing,
        reading__lte=reading,
        listening__lte=listening,
        is_active=True
    ).values_list('course', flat=True)
    print("Courses after English test filter: ", english_tests)

    return Course.objects.filter(id__in=english_tests)
