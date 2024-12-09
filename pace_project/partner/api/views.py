from rest_framework.views import APIView

from pace_project.partner.api.serializers import CourseSerializer
from pace_project.paceapp.models import Course
from rest_framework.response import Response
from rest_framework import status


class DirectApplyCourseAPIView(APIView):
    def post(self, request):
        university_id = request.data.get('university_id')
        intake_id = request.data.get('intake_id')
        level_id = request.data.get('level_id')

        queryset = Course.objects.filter(is_active=True)

        # Apply filters based on the provided IDs
        if university_id:
            queryset = queryset.filter(university_id=university_id)
        if intake_id:
            queryset = queryset.filter(intake__id=intake_id)
        if level_id:
            queryset = queryset.filter(level_id=level_id)

        # Serialize and return the filtered queryset
        serializer = CourseSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
