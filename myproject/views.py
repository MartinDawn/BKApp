from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.views import View
from django.http import JsonResponse
import requests
from allauth.socialaccount.models import SocialAccount
from rest_framework.response import Response
from rest_framework import status

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        social = user.socialaccount_set.first()
        extra = social.extra_data if social else {}

        # user_data = {field.name: getattr(user, field.name) for field in user._meta.fields}
        # print(user_data)
        # print(social.extra_data)
        return Response({
            "id": user.id,
            "email": extra.get("email"),
            "username": user.username,
            "first_name": user.first_name,
            "profile_picture": extra.get("picture"),
            "name": extra.get("name"),
        })

