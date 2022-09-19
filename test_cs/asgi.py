import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_cs.settings')
django.setup()



from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.core.asgi import get_asgi_application


import main.routing
import casebattle.routing
import crash.routing


django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            main.routing.websocket_urlpatterns +
            casebattle.routing.websocket_urlpatterns +
            crash.routing.websocket_urlpatterns
        )
    )
})
