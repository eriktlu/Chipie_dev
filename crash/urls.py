from django.urls import path, include
from . import views

app_name = "crash"

urlpatterns = [
    path('', views.crash, name="crash"),
    # path('create-battle/', views.createBattle, name="create-battle"),
    # path('rooms/<str:room_name>/', views.battleRoom, name="battle-room"),
]