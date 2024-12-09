from django.contrib import messages
from notifications.signals import notify


from pace_project.core.emails import send_partner_assessment_email
from pace_project.core.models.application_models import ApplicationRemark
from pace_project.core.models.core_models import StatusType, AssessmentRequest
from pace_project.paceapp.actstream import total_assessment, sent_assessment
from pace_project.paceapp.models import Course, EntryCriteria, EnglishTest, PGEntryCriteria, UniBoardGap, \
    AssessmentDiscovery
import logging
from django.db import transaction
from django.core.exceptions import ValidationError

from pace_project.users.middlewares import get_current_request
from pace_project.users.models import Student, UGStudentAcademic, PGStudentAcademic, Partner
from pace_project.utils.helper import create_generic_remark
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def validate_and_convert(values):
    try:
        return [int(value) if value else None for value in values]
    except (ValueError, TypeError):
        return None


def add_course_entry_criteria(*, course: Course, form_data):
    fields = ['country', 'board', 'tenth_math', 'twelfth_math', 'twelfth_english', 'overall', 'best_four']
    data = [form_data.getlist(field) for field in fields]

    feedback = {
        'success': [],
        'errors': []
    }

    with transaction.atomic():
        for values in zip(*data):
            if None in values:
                feedback['errors'].append(f"Missing value(s) found: {values}")
                logger.error(f"Missing value(s) found: {values}")
                continue

            validated_values = validate_and_convert(values)
            if validated_values is None or None in validated_values:
                feedback['errors'].append(f"Error: all fields are mandatory!")
                logger.error(f"Error: all fields are mandatory!")
                continue

            try:
                ec_instance = EntryCriteria.objects.create(
                    course=course,
                    country_id=validated_values[0],
                    board_id=validated_values[1],
                    tenth_math_marks=validated_values[2],
                    twelfth_math_marks=validated_values[3],
                    twelfth_english_marks=validated_values[4],
                    overall_marks=validated_values[5],
                    best_four_marks=validated_values[6]
                )
                success_msg = f"Entry Criteria added successfully for this course!"
                logger.info(success_msg)
                feedback['success'].append(success_msg)
            except ValidationError as e:
                error_msg = f"Validation error adding Entry Criteria for this course!"
                logger.error(error_msg)
                feedback['errors'].append(error_msg)
            except Exception as e:
                error_msg = f"Error adding EntryCriteria for this course!"
                logger.error(error_msg)
                feedback['errors'].append(error_msg)
                transaction.set_rollback(True)
                break

    return feedback


def add_pg_course_entry_criteria(*, course: Course, form_data):
    fields = ['country', 'board', 'twelfth_english', 'diploma_overall_marks', 'ug_overall_marks', 'level_diploma_marks']
    data = [form_data.getlist(field) for field in fields]

    feedback = {
        'success': [],
        'errors': []
    }

    with transaction.atomic():
        for values in zip(*data):
            if None in values:
                feedback['errors'].append(f"Missing value(s) found: {values}")
                logger.error(f"Missing value(s) found: {values}")
                continue

            validated_values = validate_and_convert(values)
            if validated_values is None or None in validated_values:
                feedback['errors'].append(f"Error: all fields are mandatory!")
                logger.error(f"Error: all fields are mandatory!")
                continue

            try:
                ec_instance = PGEntryCriteria.objects.create(
                    course=course,
                    country_id=validated_values[0],
                    board_id=validated_values[1],
                    twelfth_english_marks=validated_values[2],
                    diploma_overall_marks=validated_values[3],
                    ug_overall_marks=validated_values[4],
                    level_diploma_marks=validated_values[5],
                )
                success_msg = f"Entry Criteria added successfully for this course!"
                logger.info(success_msg)
                feedback['success'].append(success_msg)
            except ValidationError as e:
                error_msg = f"Validation error adding Entry Criteria for this course!"
                logger.error(error_msg)
                feedback['errors'].append(error_msg)
            except Exception as e:
                error_msg = f"Error adding EntryCriteria for this course!"
                logger.error(error_msg)
                feedback['errors'].append(error_msg)
                transaction.set_rollback(True)
                break

    return feedback


def add_course_english_test(*, course: Course, form_data):
    fields = ['test_country_id', 'test_type_id', 'english_test_overall', 'speaking', 'listening', 'writing', 'reading']
    data = [form_data.getlist(field) for field in fields]

    feedback = {
        'success': [],
        'errors': []
    }

    with transaction.atomic():
        for values in zip(*data):
            if None in values:
                feedback['errors'].append(f"Missing value(s) found: {values}")
                logger.error(f"Missing value(s) found: {values}")
                continue

            validated_values = validate_and_convert(values)
            if validated_values is None or None in validated_values:
                feedback['errors'].append(f"Error: all fields are mandatory!")
                logger.error(f"Error: all fields are mandatory!")
                continue

            try:
                et_instance = EnglishTest.objects.create(
                    course=course,
                    country_id=validated_values[0],
                    type_id=validated_values[1],
                    overall=validated_values[2],
                    speaking=validated_values[3],
                    listening=validated_values[4],
                    writing=validated_values[5],
                    reading=validated_values[6]
                )
                success_msg = f"EnglishTest added successfully for this course!"
                logger.info(success_msg)
                feedback['success'].append(success_msg)
            except ValidationError as e:
                error_msg = f"Validation error adding EnglishTest for the course!"
                logger.error(error_msg)
                feedback['errors'].append(error_msg)
            except Exception as e:
                error_msg = f"Error adding EnglishTest for the course!"
                logger.error(error_msg)
                feedback['errors'].append(error_msg)
                transaction.set_rollback(True)
                break

    return feedback


def is_duplicate_university_board_gap(form):
    required_fields = ['university', 'board', 'state', 'gap']

    if all(form.cleaned_data.get(field) for field in required_fields):
        return UniBoardGap.objects.filter(
            university=form.cleaned_data['university'],
            board=form.cleaned_data['board'],
            state=form.cleaned_data['state'],
            gap=form.cleaned_data['gap'],
            is_active=True
        ).exists()

    return False


def save_ug_student_academics(*, student: Student, form_data):
    """
    Save the academic details of an undergraduate student for use in later assessment discoveries.
    """
    # Extract form data into a dictionary
    fields = [
        "country_id", "board_id", "state_id", "stream_id", "sub_stream_id",
        "passing_month", "year_id", "tenth_marks", "academic_pathway",
        "diploma_overall", "twelfth_overall", "twelfth_math_marks",
        "twelfth_eng_marks", "best_four_marks", "english_test_id",
        "eng_test_overall", "speaking", "writing", "reading", "listening"
    ]
    data = {field: form_data.get(field) for field in fields}

    # Create UGStudentAcademic instance with basic details
    academic_record = UGStudentAcademic.objects.create(
        student=student,
        country_id=data["country_id"],
        board_id=data["board_id"],
        state_id=data["state_id"],
        stream_id=data["stream_id"],
        sub_stream_id=data["sub_stream_id"],
        passing_month=data["passing_month"],
        passing_year_id=data["year_id"],
        tenth_marks=data["tenth_marks"],
        academic_pathway=data["academic_pathway"],
    )

    # Set marks based on academic pathway
    if data["academic_pathway"] == 'diploma' and data["diploma_overall"]:
        academic_record.overall_marks = data["diploma_overall"]
    elif data["academic_pathway"] == 'intermediate' and data["twelfth_overall"]:
        academic_record.overall_marks = data["twelfth_overall"]
        academic_record.twelfth_math_marks = data["twelfth_math_marks"]
        academic_record.twelfth_english_marks = data["twelfth_eng_marks"]
        academic_record.twelfth_best_four_marks = data["best_four_marks"]

    # Save the initial instance
    academic_record.save()

    # Set English test details if available
    if data["english_test_id"]:
        academic_record.english_test_type_id = data["english_test_id"]
        academic_record.english_overall = data["eng_test_overall"]
        academic_record.speaking = data["speaking"]
        academic_record.writing = data["writing"]
        academic_record.reading = data["reading"]
        academic_record.listening = data["listening"]
        academic_record.save()


def save_pg_student_academics(*, student: Student, form_data):
    """
        Save the academic details of a postgraduate student for use in later assessment discoveries.
    """
    # Extract form data into a dictionary
    fields = [
        "country_id", "board_id", "state_id", "stream_id", "sub_stream_id",
        "passing_month", "year_id", "academic_pathway", "twelfth_eng_marks",
        "diploma_overall", "ug_overall", "level_diploma", "english_test_id",
        "eng_test_overall", "speaking", "writing", "reading", "listening"
    ]
    data = {field: form_data.get(field) for field in fields}

    # Create UGStudentAcademic instance with basic details
    academic_record = PGStudentAcademic.objects.create(
        student=student,
        country_id=data["country_id"],
        board_id=data["board_id"],
        state_id=data["state_id"],
        stream_id=data["stream_id"],
        sub_stream_id=data["sub_stream_id"],
        passing_month=data["passing_month"],
        passing_year_id=data["year_id"],
        academic_pathway=data["academic_pathway"],
    )

    # Set marks based on academic pathway
    if data["academic_pathway"] == 'intermediate_ug' and data["twelfth_eng_marks"]:
        academic_record.twelfth_english_marks = data["twelfth_eng_marks"]
        academic_record.ug_overall_marks = data["ug_overall"]

    elif data["academic_pathway"] == 'diploma_ug' and data["diploma_overall"]:
        academic_record.diploma_overall_marks = data["diploma_overall"]
        academic_record.ug_overall_marks = data["ug_overall"]

    elif data["academic_pathway"] == 'level_diploma' and data["level_diploma"]:
        academic_record.level_diploma_marks = data["level_diploma"]

    # Save the initial instance
    academic_record.save()

    # Set English test details if available
    if data["english_test_id"]:
        academic_record.english_test_type_id = data["english_test_id"]
        academic_record.english_overall = data["eng_test_overall"]
        academic_record.speaking = data["speaking"]
        academic_record.writing = data["writing"]
        academic_record.reading = data["reading"]
        academic_record.listening = data["listening"]
        academic_record.save()


def record_discovered_assessments(*, student_id, courses):
    if student_id:
        instance, created = AssessmentDiscovery.objects.get_or_create(student_id=student_id)
        if instance and courses:
            instance.courses.clear()
            for item in courses:
                instance.courses.add(item)


def process_assessments(*, student, user, course_ids, intake_ids, year_ids, remark):
    assessment_request = AssessmentRequest.objects.filter(student=student).first()
    for course_id, intake_id, year_id in zip(course_ids, intake_ids, year_ids):
        assessment = AssessmentDiscovery.objects.create(
            student=student,
            course_id=course_id,
            intake_id=intake_id,
            year_id=year_id,
            created_by=user
        )
        if assessment_request:
            assessment_request.assessment = assessment
            assessment_request.assessment_officer = user
            assessment_request.save()
        sent_assessment(user, assessment)
        total_assessment(user, student)
        notify_partner_on_assessment_send(assessment=assessment)
    create_generic_remark(content_object=student, remark=remark, created_by=user)


def update_student_assessment_status(*, request, student, status):
    try:
        assessment_sent_status = StatusType.objects.get(name=status)
        student.assessment_status = assessment_sent_status
        student.save()
    except StatusType.DoesNotExist:
        messages.error(request, f"{status} Status type not found. Contact to IT Administration!")


def notify_partner_on_assessment_send(*, assessment: AssessmentDiscovery):
    student = assessment.student
    if student.partner.user:
        verb = f"New assessment received of {student}!"
        request = get_current_request()
        user = request.user
        notify.send(
            sender=user,
            recipient=student.partner.user,
            verb=verb,
            target=student,
        )

    if student.partner.email:
        send_partner_assessment_email(assessment=assessment)


def notify_partner_on_message_sent(*, app_remark: ApplicationRemark):
    receiver_user = app_remark.application.student.partner.user
    if receiver_user and app_remark:
        verb = (
            f"You have a new message regarding the application of {app_remark.application.student.get_full_name}."
            f" Please check it at your earliest convenience."
        )
        notify.send(sender=app_remark.author, recipient=receiver_user, verb=verb, action_object=app_remark)
