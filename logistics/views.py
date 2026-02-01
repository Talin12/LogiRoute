from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from celery.result import AsyncResult
from .tasks import calculate_route_async

from .models import LocationNode, RouteEdge, Package
from .serializers import (
    LocationNodeSerializer,
    RouteEdgeSerializer,
    PackageSerializer,
    RouteCalculationRequestSerializer,
    PackageStateTransitionSerializer
)
from .services.graph_engine import RouteCalculator


class LocationNodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing location nodes.
    
    list: Get all location nodes
    retrieve: Get a specific location node
    create: Create a new location node
    update: Update a location node
    destroy: Delete a location node
    """
    queryset = LocationNode.objects.all()
    serializer_class = LocationNodeSerializer
    
    def get_queryset(self):
        queryset = LocationNode.objects.all()
        
        # Filter by node type if provided
        node_type = self.request.query_params.get('type', None)
        if node_type:
            queryset = queryset.filter(node_type=node_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class RouteEdgeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing route edges.
    """
    queryset = RouteEdge.objects.all()
    serializer_class = RouteEdgeSerializer
    
    def get_queryset(self):
        queryset = RouteEdge.objects.select_related('source', 'destination')
        
        # Filter by status if provided
        route_status = self.request.query_params.get('status', None)
        if route_status:
            queryset = queryset.filter(status=route_status)
        
        # Filter by source location
        source_id = self.request.query_params.get('source', None)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        
        return queryset.order_by('source__name', 'destination__name')


class PackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing packages.
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    
    def get_queryset(self):
        queryset = Package.objects.select_related(
            'origin', 'current_location', 'destination'
        )
        
        # Filter by state if provided
        package_state = self.request.query_params.get('state', None)
        if package_state:
            queryset = queryset.filter(state=package_state)
        
        # Filter by tracking ID
        tracking_id = self.request.query_params.get('tracking_id', None)
        if tracking_id:
            queryset = queryset.filter(tracking_id=tracking_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """
        Handle package state transitions using FSM.
        
        POST /api/packages/{id}/transition/
        Body: {"action": "start_transit", "new_location_id": 2}
        """
        package = self.get_object()
        serializer = PackageStateTransitionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action_name = serializer.validated_data['action']
        new_location_id = serializer.validated_data.get('new_location_id')
        
        try:
            # Execute the FSM transition
            if action_name == 'start_transit':
                package.start_transit()
            elif action_name == 'move_to_location':
                if not new_location_id:
                    return Response(
                        {'error': 'new_location_id required for move_to_location'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                new_location = get_object_or_404(LocationNode, id=new_location_id)
                package.move_to_location(new_location)
            elif action_name == 'start_delivery':
                package.start_delivery()
            elif action_name == 'complete_delivery':
                package.complete_delivery()
            elif action_name == 'cancel':
                package.cancel_package()
            
            package.save()
            
            return Response(
                PackageSerializer(package).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Transition failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
def calculate_route(request):
    """
    Calculate the optimal route between two locations.
    
    POST /api/calculate-route/
    Body: {
        "source_id": 1,
        "destination_id": 5,
        "optimize_by": "time"  # optional: time, distance, or cost
    }
    """
    serializer = RouteCalculationRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    source_id = serializer.validated_data['source_id']
    destination_id = serializer.validated_data['destination_id']
    optimize_by = serializer.validated_data.get('optimize_by', 'time')
    
    # Use the graph engine to calculate route
    calculator = RouteCalculator()
    result = calculator.calculate_shortest_path(
        source_id=source_id,
        destination_id=destination_id,
        optimize_by=optimize_by
    )
    
    if result['status'] == 'error':
        return Response(
            result,
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_reachable_destinations(request, location_id):
    """
    Get all destinations reachable from a given location.
    
    GET /api/locations/{location_id}/reachable/
    """
    calculator = RouteCalculator()
    result = calculator.get_all_routes_from_location(location_id)
    
    if result['status'] == 'error':
        return Response(
            result,
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def track_package(request, tracking_id):
    """
    Track a package by its tracking ID.
    
    GET /api/track/{tracking_id}/
    """
    try:
        package = Package.objects.select_related(
            'origin', 'current_location', 'destination'
        ).get(tracking_id=tracking_id)
        
        # Calculate route if package is in transit
        route_info = None
        if package.state in ['pending', 'in_transit', 'out_for_delivery']:
            calculator = RouteCalculator()
            route_result = calculator.calculate_shortest_path(
                source_id=package.current_location_id,
                destination_id=package.destination_id,
                optimize_by='time'
            )
            if route_result['status'] == 'success':
                route_info = route_result['route']
        
        return Response({
            'package': PackageSerializer(package).data,
            'route': route_info
        }, status=status.HTTP_200_OK)
        
    except Package.DoesNotExist:
        return Response(
            {'error': f'Package with tracking ID {tracking_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
def calculate_route_async_view(request):
    """
    Async route calculation - returns task ID immediately.
    Client can poll /api/task-status/{task_id}/ for result.
    
    POST /api/calculate-route-async/
    Body: {
        "source_id": 1,
        "destination_id": 5,
        "optimize_by": "time"
    }
    """
    serializer = RouteCalculationRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    source_id = serializer.validated_data['source_id']
    destination_id = serializer.validated_data['destination_id']
    optimize_by = serializer.validated_data.get('optimize_by', 'time')
    
    # Start async task
    task = calculate_route_async.delay(source_id, destination_id, optimize_by)
    
    return Response({
        'task_id': task.id,
        'status': 'processing',
        'check_status_url': f'/api/task-status/{task.id}/'
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def task_status(request, task_id):
    """
    Check status of an async task.
    
    GET /api/task-status/{task_id}/
    """
    task = AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting to be processed'
        }
    elif task.state == 'PROCESSING':
        response = {
            'state': task.state,
            'status': task.info.get('status', 'Processing...')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': 'Unknown state'
        }
    
    return Response(response)