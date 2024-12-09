import threading
from django.contrib.messages import get_messages, add_message

_thread_locals = threading.local()


def get_current_request():
    return ThreadLocalMiddleware.get_current_request()


def get_current_messages():
    request = get_current_request()
    if request:
        return get_messages(request)
    return None


def add_current_message(level, message):
    request = get_current_request()
    if request:
        add_message(request, level, message)


class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response

    @staticmethod
    def get_current_request():
        return getattr(_thread_locals, 'request', None)
