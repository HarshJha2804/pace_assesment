import json

from django.http import JsonResponse
from django.core.serializers import serialize
from pace_project.paceapp.models import State


def ajax_state_by_country_view(request):
    country_id = request.GET.get('country_id')

    if not country_id:
        return JsonResponse({"status": "error", "message": "No country ID passed!"}, status=400)

    states = State.objects.filter(country_id=country_id)

    if states.exists():
        serialized_states = serialize('json', states)
        parsed_states = json.loads(serialized_states)
        return JsonResponse({"status": "success", "states": parsed_states}, status=200, safe=False)

    return JsonResponse({"status": "no_states", "message": "No states available for the selected country."}, status=200)
