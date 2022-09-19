"""test_cs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
from main import views

# router = routers.DefaultRouter()
# router.register(r'customuser', views.CustomUserView, 'customUser')
# router.register(r'message', views.MessageView, 'message')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('deposit/', include('deposit.urls')),
    path('withdraw/', include('withdraw.urls')),
    path('casebattle/', include('casebattle.urls')),
    path('crash/', include('crash.urls')),
    # path('api/', include(router.urls))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)
