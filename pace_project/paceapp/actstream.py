from actstream.actions import action
from pace_project.core.models.application_models import Application
from pace_project.core.models.core_models import StatusType
from pace_project.paceapp.enums import RoleEnum, ActivityStreamVerb
from datetime import datetime, timedelta
from actstream.models import Action
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from pace_project.users.models import Student

User = get_user_model()


def get_stream_data(user):
    actions_json = []
    try:
        three_days_ago = datetime.now() - timedelta(days=3)
        user_actions = Action.objects.filter(actor_object_id=user, timestamp__gte=three_days_ago)
        user_actions = user_actions.order_by('-timestamp')
        verb_counts = defaultdict(int)
        for verb_data in user_actions:
            verb_counts[verb_data.verb] += 1
        for data in user_actions:
            full_name = data.target.get_full_name if hasattr(data.target, 'get_full_name') else str(data.target)
            action_data = {
                'actor': str(data.actor),
                'verb': data.verb,
                'target': str(full_name),
                'action_object': str(data.action_object),
                'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),

            }
            actions_json.append(action_data)
        actions_json.append({"total_count_data": {verb: count for verb, count in verb_counts.items()}})
        return actions_json
    except Exception:
        return actions_json


def total_assessment(user, student):
    student_content_type = ContentType.objects.get_for_model(Student)
    three_days_ago = datetime.now() - timedelta(days=3)
    existing_total_action = Action.objects.filter(
        actor_object_id=user.id,
        target_object_id=student.id,
        target_content_type=student_content_type,
        verb=ActivityStreamVerb.TOTAL_ASSESSMENT.value,
        timestamp__gte=three_days_ago
    ).exists()
    if not existing_total_action:
        Action.objects.create(
            actor=user,
            verb=ActivityStreamVerb.TOTAL_ASSESSMENT.value,
            description="New assessment added for ",
            target=student,
            action_object=student
        )


def sent_assessment(user, assessment):
    student_content_type = ContentType.objects.get_for_model(Student)
    three_days_ago = datetime.now() - timedelta(days=3)
    existing_action = Action.objects.filter(
        actor_object_id=user.id,
        target_object_id=assessment.student.id,
        target_content_type=student_content_type,
        verb=ActivityStreamVerb.SENT_ASSESSMENT.value,
        timestamp__gte=three_days_ago
    ).exists()
    if not existing_action:
        Action.objects.create(
            actor=user,
            verb=ActivityStreamVerb.SENT_ASSESSMENT.value,
            target=assessment.student,
            action_object=assessment
        )


def reject_assessment(user, student):
    try:
        action.send(user, verb=ActivityStreamVerb.REJECTED_ASSESSMENT.value,
                    description="Assessment rejected",
                    target=student,
                    action_object=student,
                    add_assessment_added=True
                    )
    except Exception as e:
        print("Error occurred while rejecting assessment:", e)


def generate_new_application_stream(*, current_user: User, application: Application, assessment_id=None, is_direct=False):
    action.send(
        current_user,
        verb="Application applied",
        action_object=application.current_status,
        target=application,
        direct_application=is_direct,
        application_action="Apply",
        assessment_id=assessment_id,
    )


def generate_updated_application_stream(*, current_user: User, previous_status, application: Application):
    action.send(
        current_user,
        verb="Application status updated",
        action_object=application.current_status,
        target=application,
        application_prev_status=previous_status,
        application_action="Update"
    )
