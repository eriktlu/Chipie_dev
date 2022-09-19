from django.urls import path, include
from . import views

app_name = "casebattle"

urlpatterns = [
    path('', views.caseBattle, name="casebattle"),
    path('create-battle/', views.createBattle, name="create-battle"),
    path('rooms/<str:room_name>/', views.battleRoom, name="battle-room"),
]