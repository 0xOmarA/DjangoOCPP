from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ocpp/(?P<charger_id>\w+)/$', consumers.OcppConsumer.as_asgi()),
    re_path(r'ws/external_control/(?P<charger_id>\w+)/$', consumers.ExternalCommandsConsumer.as_asgi()),
]