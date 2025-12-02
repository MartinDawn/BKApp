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

from django.conf import settings
from django.conf.urls.static import static

from users.views import GoogleLogin, MeView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView  
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/social/login/', GoogleLogin.as_view(), name='google_login'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/', include('store.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Endpoint giao diện Swagger UI (Giao diện phổ biến nhất)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Endpoint giao diện Redoc (Giao diện thay thế, gọn gàng hơn)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Google Sign-In SDK dành cho React Native để xử lý đăng nhập, bên dưới là client_id
# 48475528916-v4j2qg40mtqlt256iige8pj4nrk0nr9h.apps.googleusercontent.com