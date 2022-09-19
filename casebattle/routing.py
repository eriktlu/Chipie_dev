from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/cb/<str:room_name>/', consumers.CaseBattleConsumer.as_asgi()),
]