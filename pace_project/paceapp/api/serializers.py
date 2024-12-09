from rest_framework import serializers
from pace_project.paceapp.models import Campus, Board, State, University, Country, Level, Stream, EnglishTestType, \
    SubStream, Course, UniversityIntake, Intake


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id', 'country_name', 'country_code'
        ]


class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = '__all__'


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'country']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'level']


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['id', 'stream']


class SubStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubStream
        fields = ['id', 'sub_stream_name']


class EnglishTestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishTestType
        fields = ['id', 'english_test_name']


class IntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intake
        fields = ['id', 'intake_month']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']


class UniversityIntakeSerializer(serializers.ModelSerializer):
    intakes = IntakeSerializer(many=True)

    class Meta:
        model = UniversityIntake
        fields = ['id', 'intakes']
