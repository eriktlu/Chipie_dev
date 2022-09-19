from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/game/crash/', consumers.CrashConsumer.as_asgi()),
    path('ws/game/crash_bet/', consumers.CrashBetConsumer.as_asgi()),
]