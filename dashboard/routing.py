from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/phone-mouse/$', consumers.PhoneMouseConsumer.as_asgi()),
]
