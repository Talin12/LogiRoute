from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/track/(?P<tracking_id>[\w-]+)/$', consumers.PackageTrackingConsumer.as_asgi()),
    re_path(r'^ws/routes/$', consumers.RouteVisualizationConsumer.as_asgi()),
]
