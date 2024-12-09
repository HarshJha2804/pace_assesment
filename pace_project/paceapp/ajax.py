import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Campus, Board, State, Country, University, Stream, UniversityStateMapping, Level, Intake, \
    UniversityIntake


def get_campuses(request):
    country_id = request.GET.get('country_id')
    if country_id:
        campuses = Campus.objects.filter(country_id=country_id)
        data = [{'id': campus.id, 'name': campus.name} for campus in campuses]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_board_or_state(request):
    if request.method == "POST":
        data = json.loads(request.body)
        countries = data.get('countries')
        boards = Board.objects.filter(country_id__in=countries)
        states = State.objects.filter(country_id__in=countries)
        data = {
            'boards': [{'id': board.id, 'name': board.name} for board in boards],
            'states': [{'id': state.id, 'name': state.name} for state in states],
        }
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_other_countries(request):
    country_id = request.GET.get('country_id')
    if country_id:
        other_countries = Country.objects.exclude(id=country_id)
        data = [{'id': country.id, 'name': country.country_name} for country in other_countries]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def ajax_get_universities(request):
    country_id = request.GET.get('country_id')
    if country_id:
        universities = University.objects.filter(country_id=country_id)
        data = {
            'universities': [{'id': university.id, 'name': university.name} for university in universities]
        }
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def ajax_get_university_intakes(request):
    university_id = request.GET.get('university_id')
    response_data = {
        'intakes': []
    }
    if university_id:
        intakes = UniversityIntake.objects.filter(university_id=university_id, is_active=True).first().intakes.all()
        if intakes:
            response_data['intakes'] = [
                {'id': intake.id, 'name': intake.intake_month} for intake in intakes
            ]
        else:
            response_data['error'] = "No active intakes found for this university."

    return JsonResponse(response_data)


def ajax_get_stream_or_campus(request):
    university_id = request.GET.get('university_id')
    university = get_object_or_404(University, id=university_id)
    if university:
        campuses = university.campus.all()
        unique_uniset = UniversityStateMapping.objects.filter(university=university, is_active=True)
        distinct_stream_ids = unique_uniset.values_list('streams').distinct()
        streams = Stream.objects.filter(pk__in=distinct_stream_ids)
        data = {
            'campus': [{'id': campus.id, 'name': campus.name} for campus in campuses],
            'streams': [{'id': stream.id, 'name': stream.stream} for stream in streams],
        }
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def ajax_get_streams(request):
    if request.method == "POST":
        data = json.loads(request.body)
        university_id = data.get('university')
        level_id = data.get('level')
        unique_uniset = UniversityStateMapping.objects.filter(university_id=university_id, is_active=True)
        distinct_stream_ids = unique_uniset.values_list('streams').distinct()
        level_object = get_object_or_404(Level, pk=level_id)
        streams = level_object.streams.filter(pk__in=distinct_stream_ids)
        data = {
            'streams': [{'id': stream.id, 'name': stream.stream} for stream in streams]
        }
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def ajax_get_substream(request):
    stream_id = request.GET.get('stream_id')
    if stream_id:
        stream = get_object_or_404(Stream, id=stream_id)
        substreams = stream.sub_stream.filter(is_active=True)
        data = {
            'sub_stream': [{'id': substream.id, 'name': substream.sub_stream_name} for substream in substreams]
        }
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)
