from django.core.serializers import serialize
from django.http import JsonResponse
import json
from django.core.cache import cache


def mark_all_as_read_ajax(request):
    """
    Mark all notifications all as read.
    """
    user = request.user
    user.notifications.mark_all_as_read()
    count = user.notifications.unread().count()
    response_data = {'unread_count': count}
    return JsonResponse(response_data, status=200)


def get_notifications_ajax(request):
    """
    Filtering Read and unread notifications
    """
    user = request.user

    notifications = get_cached_notifications(user=user)

    serialized_notifications = serialize('json', notifications)
    parsed_notifications = json.loads(serialized_notifications)
    return JsonResponse(parsed_notifications, safe=False)


def get_cached_notifications(*, user):
    cache_key = f"user_notifications_{user.id}"
    notifications = cache.get(cache_key)
    if notifications is None:
        unread_notifications = list(user.notifications.unread())
        read_notifications = list(user.notifications.read())

        # Combine unread and read notifications, showing unread first
        notifications = unread_notifications + read_notifications

        cache.set(cache_key, notifications, timeout=300)  # Cache for 300 seconds

    return notifications
