"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from .views import GoogleLogin
from .views import MeView
urlpatterns = [
    path('auth/social/login/', GoogleLogin.as_view(), name='google_login'),
    path('api/me/', MeView.as_view(), name='me'),
]
# Google Sign-In SDK dành cho React Native để xử lý đăng nhập, bên dưới là client_id
# 48475528916-v4j2qg40mtqlt256iige8pj4nrk0nr9h.apps.googleusercontent.com