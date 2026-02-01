from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'locations', views.LocationNodeViewSet, basename='location')
router.register(r'routes', views.RouteEdgeViewSet, basename='route')
router.register(r'packages', views.PackageViewSet, basename='package')

urlpatterns = [
    # Router URLs (viewsets)
    path('', include(router.urls)),
    
    # Custom endpoints
    path('calculate-route/', views.calculate_route, name='calculate-route'),
    path('locations/<int:location_id>/reachable/', views.get_reachable_destinations, name='reachable-destinations'),
    path('track/<str:tracking_id>/', views.track_package, name='track-package'),
    path('calculate-route-async/', views.calculate_route_async_view, name='calculate-route-async'),
    path('task-status/<str:task_id>/', views.task_status, name='task-status'),
]