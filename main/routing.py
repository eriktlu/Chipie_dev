from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),
    path('ws/game/roulette/', consumers.RouletteGame.as_asgi()),
    path('ws/game/roulette_bet/', consumers.RouletteBet.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]