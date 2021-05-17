from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from calling.consumers import ChatConsumer
application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    #url("calling/interface/<uuid:session_id>", ChatConsumer.as_asgi()),
                    url("calling/interface/", ChatConsumer.as_asgi()),
                    #url("calling/webhook/", testConsumer()),
                ]
            )
        )
    )
})