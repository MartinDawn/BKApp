from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.views import View
from django.http import JsonResponse
import requests
from allauth.socialaccount.models import SocialAccount
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

# --- Import serializer mới ---
from .serializers import ProfileUpdateSerializer


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_data(self, user):
        """Hàm trợ giúp để lấy dữ liệu user (bao gồm cả profile)"""
        social = user.socialaccount_set.first()
        extra = social.extra_data if social else {}
        
        # 'user.profile' đã tồn tại nhờ tín hiệu (signal)
        # Lấy profile, nếu chưa có thì TẠO MỚI ngay lập tức
        from users.models import Profile # Đảm bảo bạn đã import model Profile
        profile, created = Profile.objects.get_or_create(user=user) 

        return {
            "id": user.id,
            "email": extra.get("email") or user.email,
            "username": user.username,
            "first_name": user.first_name,
            "profile_picture": extra.get("picture"),
            "name": extra.get("name") or user.get_full_name(),
            
            # --- Thêm trường address vào GET ---
            "address": profile.address ,
            "rating": profile.rating,
            "num_reviews": profile.num_reviews,

        }

    def get(self, request):
        """
        API GET: Trả về thông tin của user.
        """
        data = self.get_user_data(request.user)
        return Response(data)

    def patch(self, request):
        """
        API PATCH: Cập nhật thông tin cho user (ví dụ: address).
        """
        user = request.user
        # Lấy profile, nếu chưa có thì TẠO MỚI ngay lập tức
        from users.models import Profile # Đảm bảo bạn đã import model Profile
        profile, created = Profile.objects.get_or_create(user=user) # Lấy profile của user

        # Dùng serializer mới để cập nhật 'profile'
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True) 
        
        if serializer.is_valid():
            serializer.save()
            # Trả về thông tin user ĐÃ được cập nhật
            updated_data = self.get_user_data(user)
            return Response(updated_data)
        
        # Nếu dữ liệu không hợp lệ
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """Trả về thông tin public của một user theo `user_id`.

    Thông tin gồm: id, username, first_name, name, profile_picture,
    address, rating, num_reviews. Email chỉ trả về nếu requester là chính
    user hoặc staff.
    """
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        social = user.socialaccount_set.first()
        extra = social.extra_data if social else {}

        from users.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)

        # Expose email only when requester is the same user or staff
        email = None
        if request.user.is_authenticated and (request.user.id == user.id or request.user.is_staff):
            email = user.email

        data = {
            "id": user.id,
            "email": email,
            "username": user.username,
            "first_name": user.first_name,
            "profile_picture": extra.get("picture"),
            "name": extra.get("name") or user.get_full_name(),
            "address": profile.address,
            "rating": profile.rating,
            "num_reviews": profile.num_reviews,
        }

        return Response(data)