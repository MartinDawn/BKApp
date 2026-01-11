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
from rest_framework.authtoken.models import Token
from django.conf import settings

# --- Import serializer mới ---
from .serializers import ProfileUpdateSerializer


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    
    def post(self, request, *args, **kwargs):
        """Accept an `idToken` from frontend, verify with Google, create/get user and return DRF Token."""
        id_token = None
        # The frontend may send the token in various keys
        for key in ("idToken", "id_token", "idtoken"):
            if request.data.get(key):
                id_token = request.data.get(key)
                break

        if not id_token:
            return Response({"detail": "idToken is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token with Google's tokeninfo endpoint
        resp = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token})
        if resp.status_code != 200:
            return Response({"detail": "Invalid idToken."}, status=status.HTTP_400_BAD_REQUEST)

        payload = resp.json()


        uid = payload.get("sub")
        email = payload.get("email")
        if not uid or not email:
            return Response({"detail": "idToken missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Require edu.vn email domain
        if not email.lower().endswith("edu.vn"):
            return Response({"detail": "Bạn phải dùng email sinh viên để đăng nhập và đăng kí."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or get a local user
        username_base = email.split("@")[0]
        username = username_base
        # Ensure unique username
        counter = 0
        while User.objects.filter(username=username).exists():
            counter += 1
            username = f"{username_base}_{counter}"

        user, created = User.objects.get_or_create(email=email, defaults={
            "username": username,
            "first_name": payload.get("given_name", ""),
            "last_name": payload.get("family_name", ""),
        })

        if created:
            user.set_unusable_password()
            user.save()

        # Update user fields if they are missing or changed
        updated = False
        if not user.first_name and payload.get("given_name"):
            user.first_name = payload.get("given_name")
            updated = True
        if not user.last_name and payload.get("family_name"):
            user.last_name = payload.get("family_name")
            updated = True
        if updated:
            user.save()

        # Create or update SocialAccount record so other parts of app can read extra_data
        SocialAccount.objects.update_or_create(
            user=user,
            provider="google",
            uid=uid,
            defaults={"extra_data": payload},
        )

        # Create or get DRF Token
        token, _ = Token.objects.get_or_create(user=user)

        # Return token and a small user payload
        return Response({
            "key": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": payload.get("name") or user.get_full_name(),
                "profile_picture": payload.get("picture"),
            },
        })
    

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