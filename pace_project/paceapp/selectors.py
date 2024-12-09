from pace_project.paceapp.enums import LevelEnum
from pace_project.paceapp.models import AssessmentDiscovery
from pace_project.users.models import Student, UGStudentAcademic, PGStudentAcademic


def get_student_object(*, student_id: int):
    if Student.objects.filter(pk=student_id).exists():
        student = Student.objects.get(pk=student_id)
        return student
    return None


def get_student_academics(*, student: Student):
    if student.study_level.level == LevelEnum.UNDERGRADUATE.value:
        if UGStudentAcademic.objects.filter(student=student).exists():
            return UGStudentAcademic.objects.get(student=student)

    elif student.study_level.level == LevelEnum.POSTGRADUATE.value:
        if PGStudentAcademic.objects.filter(student=student).exists():
            return PGStudentAcademic.objects.get(student=student)

    return None


def get_assessment_discoveries(*, student: Student):
    try:
        return AssessmentDiscovery.objects.get(student=student)
    except AssessmentDiscovery.DoesNotExist:
        return None
