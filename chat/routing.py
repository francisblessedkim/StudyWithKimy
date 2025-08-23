from django.urls import re_path
from . import consumers  # type: ignore

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<username>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
