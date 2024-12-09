from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from pace_project.paceapp.models import Campus, Board, State, University, Country, Level, Stream, EnglishTestType, \
    SubStream, UniversityStateMapping, Course, UniversityIntake, Intake
from .serializers import CampusSerializer, BoardSerializer, StateSerializer, UniversitySerializer, CountrySerializer, \
    LevelSerializer, StreamSerializer, EnglishTestTypeSerializer, SubStreamSerializer, CourseSerializer, \
    UniversityIntakeSerializer, IntakeSerializer
from pace_project.users.models import Student


class CourseRecommendAPIView(APIView):
    def get(self, request):
        # Retrieve active instances from each model
        active_countries = Country.objects.filter(is_active=True)
        active_levels = Level.objects.all()  # Assuming there's no "is_active" field in Level model
        active_streams = Stream.objects.filter(is_active=True)
        active_english_test_types = EnglishTestType.objects.filter(is_active=True)

        student_id = request.GET.get("student_id")
        if student_id:
            if Student.objects.filter(id=student_id).exists():
                student = Student.objects.get(id=student_id)
                active_streams = student.study_level.streams.filter(is_active=True)

        # Serialize the data
        country_serializer = CountrySerializer(active_countries, many=True)
        level_serializer = LevelSerializer(active_levels, many=True)
        stream_serializer = StreamSerializer(active_streams, many=True)
        english_test_type_serializer = EnglishTestTypeSerializer(active_english_test_types, many=True)

        # Combine the serialized data into a single response
        response_data = {
            'countries': country_serializer.data,
            'levels': level_serializer.data,
            'streams': stream_serializer.data,
            'english_test_types': english_test_type_serializer.data
        }

        return Response(response_data)


class BoardsByCountryAPIView(APIView):
    def get(self, request):
        country_name = request.GET.get('country_name')
        country_id = request.GET.get('country_id')
        level_id = request.GET.get('level_id')

        if not country_name and not country_id:
            return Response({'error': 'Please provide a country_name or country_id parameter in the request.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if level_id:
            level = get_object_or_404(Level, pk=level_id)
            boards = level.boards.filter(
                Q(country_id=country_id) | Q(country__country_name__iexact=country_name),
                is_active=True
            )
        else:
            boards = Board.objects.filter(
                Q(country_id=country_id) | Q(country__country_name__iexact=country_name),
                is_active=True
            ).distinct()

        if not boards.exists():
            return Response({'error': 'No boards found for the specified country.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StatesByCountryAPIView(APIView):
    def get(self, request):
        country_name = request.GET.get('country_name')
        country_id = request.GET.get('country_id')

        if not country_name and not country_id:
            return Response({'error': 'Please provide a country_name/country_id parameter in the request.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            if country_id:
                states = State.objects.filter(country_id=country_id)
            else:
                states = State.objects.filter(country__country_name__iexact=country_name)
        except State.DoesNotExist:
            return Response({'error': 'No states found for the specified country.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StateSerializer(states, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class StreamByLevelAPIView(APIView):
    def get(self, request):
        level_id = request.GET.get("level_id")
        level_name = request.GET.get("level_name")
        if not level_id and not level_name:
            return Response(
                {'error': 'Please provide a level_id or level_name in the request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        level = None
        if level_id:
            level = get_object_or_404(Level, pk=level_id)
        elif level_name:
            level = get_object_or_404(Level, pk=level_name)

        streams = level.streams.filter(is_active=True)

        if not streams.exists():
            return Response(
                {'error': 'No streams found for the specified level.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StreamSerializer(streams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubStreamsByStreamAPIView(APIView):
    def get(self, request):
        stream_id = request.GET.get('stream_id')
        stream_name = request.GET.get('stream_name')

        if not stream_id and not stream_name:
            return Response({'error': 'Please provide either a stream_id or stream_name parameter in the request.'},
                            status=status.HTTP_400_BAD_REQUEST)

        stream = None
        if stream_id:
            stream = get_object_or_404(Stream, id=stream_id)
        elif stream_name:
            stream = get_object_or_404(Stream, stream=stream_name)

        substreams = stream.sub_stream.filter(is_active=True)

        if not substreams.exists():
            return Response({'error': 'No substreams found for the specified stream.'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = SubStreamSerializer(substreams, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseRequirementBoardListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        country_id = request.query_params.get('country_id')
        if not country_id:
            return Response({"error": "country_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, pk=course_id)
        unique_uniset = UniversityStateMapping.objects.filter(university=course.university, is_active=True)

        distinct_board_ids = unique_uniset.values('boards').distinct()
        unique_boards_queryset = course.level.boards.filter(pk__in=distinct_board_ids, country_id=country_id)

        if not unique_boards_queryset.exists():
            return Response({"error": "No boards found for the given course and country"},
                            status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginated_boards = paginator.paginate_queryset(unique_boards_queryset, request)
        serializer = BoardSerializer(paginated_boards, many=True)
        return paginator.get_paginated_response(serializer.data)


class FilterCourseAPIView(APIView):
    def post(self, request):
        serializers_data = {
            'country': CountrySerializer,
            'level': LevelSerializer,
            'board': BoardSerializer,
            'state': StateSerializer,
            'stream': StreamSerializer,
            'substream': SubStreamSerializer
        }

        errors = {}
        for field, serializer_class in serializers_data.items():
            serializer = serializer_class(data=request.data.get(field))
            if not serializer.is_valid():
                errors[field] = serializer.errors

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Data submitted successfully.'}, status=status.HTTP_200_OK)


class CourseFilterListView(APIView):

    def post(self, request):
        university_id = request.data.get('university_id')
        level_id = request.data.get('level_id')
        if not university_id or not level_id:
            return Response({"error": "University ID and Level ID are required."}, status=status.HTTP_400_BAD_REQUEST)
        courses = Course.objects.filter(university_id=university_id, level_id=level_id, is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UniversityIntakeFilterListView(APIView):

    def get(self, request, university_id):
        intakes = UniversityIntake.objects.filter(university_id=university_id, is_active=True)
        serializer = UniversityIntakeSerializer(intakes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UniversityIntakeAPIView(APIView):
    """API to filter university intakes through university id. return unique intakes with their name and id."""

    def get(self, request, university_id):
        try:
            # Fetch unique intake IDs directly
            intake_ids = UniversityIntake.objects.filter(
                university_id=university_id,
                is_active=True
            ).values_list('intakes', flat=True).distinct()

            unique_intakes = Intake.objects.filter(id__in=intake_ids)

            serializer = IntakeSerializer(unique_intakes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UniversityIntake.DoesNotExist:
            return Response({'error': 'University not found'}, status=status.HTTP_404_NOT_FOUND)
