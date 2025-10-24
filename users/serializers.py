from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer này CHỈ dùng để cập nhật 'address'
    """
    class Meta:
        model = Profile
        fields = ['address']