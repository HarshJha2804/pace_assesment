from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from config.settings.base import env
from pace_project.users.models import User

from .serializers import UserSerializer, EmpowerEDUSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class EmpowerEDUQueryAPIView(APIView):

    def post(self, request):
        serializer = EmpowerEDUSerializer(data=request.data)
        if serializer.is_valid():
            processed_data = serializer.validated_data
            self.send_query_on_email(processed_data)
            return Response("We will connect you shortly!", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_query_on_email(query_data):
        name = query_data.get("name")
        mobile_number = query_data.get("mobile_number")
        email = query_data.get("email")
        message = query_data.get("message")
        subject = f"EmpowerEDU New query of {name}"
        email_message = f"Name: {name}. \nMobile no: {mobile_number}\nEmail: {email}\nMessage: {message}"
        recipient_list = env.list("EM_EDU_QUERY_RECIPIENT_LIST", None)
        default_from = env("EMPOWER_EDU_DEFAULT_FROM", default="Empower EDU")
        send_mail(subject, email_message, from_email=default_from, recipient_list=recipient_list, fail_silently=True)

