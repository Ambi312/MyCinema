from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import CustomUser
from account.serializers import RegisterSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Successfully registered on StackOverFlow.kg', status=201)


class ActivateAPIView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('activation_code')
        user = CustomUser.objects.filter(phone_number=phone_number, activation_code=code).first()
        if not user:
            return Response('There is no such user', status=400)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('You activate your account', status=200)
from django.shortcuts import render

# Create your views here.
