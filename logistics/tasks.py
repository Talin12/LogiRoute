from celery import shared_task
from django.core.cache import cache
import time
from .services.graph_engine import RouteCalculator


@shared_task(bind=True, name='logistics.calculate_route_async')
def calculate_route_async(self, source_id, destination_id, optimize_by='time'):
    """
    Async task for route calculation.
    Used for complex graphs or when we want non-blocking API responses.
    
    Args:
        source_id: Starting location ID
        destination_id: Ending location ID
        optimize_by: Optimization criteria (time/distance/cost)
        
    Returns:
        Route calculation result
    """
    # Update task state to show progress
    self.update_state(state='PROCESSING', meta={'status': 'Building graph...'})
    
    calculator = RouteCalculator()
    
    self.update_state(state='PROCESSING', meta={'status': 'Calculating route...'})
    
    result = calculator.calculate_shortest_path(
        source_id=source_id,
        destination_id=destination_id,
        optimize_by=optimize_by
    )
    
    # Cache the result for 5 minutes
    cache_key = f'route_{source_id}_{destination_id}_{optimize_by}'
    cache.set(cache_key, result, 300)
    
    return result


@shared_task(name='logistics.rebuild_graph_cache')
def rebuild_graph_cache():
    """
    Rebuild the route graph cache.
    This can be triggered periodically or when routes are updated.
    """
    calculator = RouteCalculator()
    calculator.build_graph(force_rebuild=True)
    
    return {
        'status': 'success',
        'message': 'Graph cache rebuilt',
        'nodes': len(calculator.graph.nodes()),
        'edges': len(calculator.graph.edges())
    }


@shared_task(name='logistics.update_package_location')
def update_package_location(package_id, new_location_id):
    """
    Update package location in background.
    This simulates package movement through the network.
    """
    from .models import Package, LocationNode
    from django.shortcuts import get_object_or_404
    
    try:
        package = get_object_or_404(Package, id=package_id)
        new_location = get_object_or_404(LocationNode, id=new_location_id)
        
        # Simulate processing time
        time.sleep(1)
        
        if package.state == 'in_transit':
            package.move_to_location(new_location)
            package.save()
            
            return {
                'status': 'success',
                'package_id': package_id,
                'tracking_id': package.tracking_id,
                'new_location': new_location.name
            }
        else:
            return {
                'status': 'error',
                'message': f'Package must be in transit. Current state: {package.state}'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }