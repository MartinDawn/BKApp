# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email', '')
        print(sociallogin.account.extra_data)
        if not email.endswith('.edu.vn'):
            raise PermissionDenied("Bạn cần dùng tài khoản nhà trường để đăng nhập")
