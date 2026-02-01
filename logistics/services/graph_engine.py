import networkx as nx
from typing import Dict, List, Optional, Tuple
from logistics.models import LocationNode, RouteEdge


class RouteCalculator:
    """
    Handles graph-based route calculations using Dijkstra's algorithm.
    This is the core algorithmic engine of LogiRoute.
    """
    
    def __init__(self):
        self.graph: Optional[nx.DiGraph] = None
        self.node_data: Dict = {}
    
    def build_graph(self, force_rebuild: bool = False) -> nx.DiGraph:
        """
        Construct in-memory graph from database.
        
        Args:
            force_rebuild: If True, rebuild even if graph exists
            
        Returns:
            NetworkX directed graph
        """
        if self.graph is not None and not force_rebuild:
            return self.graph
        
        G = nx.DiGraph()
        
        # Add nodes with metadata
        nodes = LocationNode.objects.filter(is_active=True)
        for node in nodes:
            G.add_node(
                node.id,
                name=node.name,
                node_type=node.node_type,
                latitude=float(node.latitude),
                longitude=float(node.longitude),
                address=node.address
            )
            
            # Store for quick lookup
            self.node_data[node.id] = {
                'name': node.name,
                'type': node.node_type,
                'coords': (float(node.latitude), float(node.longitude))
            }
        
        # Add edges with weights
        edges = RouteEdge.objects.select_related('source', 'destination')
        
        for edge in edges:
            # Calculate weight based on status
            base_weight = edge.travel_time_minutes
            
            if edge.status == 'closed':
                # Don't add closed routes to graph
                continue
            elif edge.status == 'slow':
                # Apply 50% penalty for slow routes
                weight = base_weight * 1.5
            else:  # active
                weight = base_weight
            
            G.add_edge(
                edge.source_id,
                edge.destination_id,
                weight=weight,
                distance=float(edge.distance_km),
                cost=float(edge.cost_per_km) * edge.distance_km,
                status=edge.status,
                edge_id=edge.id
            )
        
        self.graph = G
        return G
    
    def calculate_shortest_path(
        self,
        source_id: int,
        destination_id: int,
        optimize_by: str = 'time'
    ) -> Dict:
        """
        Calculate the shortest path using Dijkstra's algorithm.
        
        Args:
            source_id: Starting location node ID
            destination_id: Ending location node ID
            optimize_by: 'time', 'distance', or 'cost'
            
        Returns:
            Dictionary with path details or error
        """
        # Build graph if not exists
        if self.graph is None:
            self.build_graph()
        
        # Validate nodes exist in graph
        if source_id not in self.graph:
            return {
                'status': 'error',
                'error': f'Source location (ID: {source_id}) not found or inactive'
            }
        
        if destination_id not in self.graph:
            return {
                'status': 'error',
                'error': f'Destination location (ID: {destination_id}) not found or inactive'
            }
        
        # Select weight attribute based on optimization preference
        weight_attr = {
            'time': 'weight',
            'distance': 'distance',
            'cost': 'cost'
        }.get(optimize_by, 'weight')
        
        try:
            # Run Dijkstra's algorithm
            path = nx.dijkstra_path(
                self.graph,
                source_id,
                destination_id,
                weight=weight_attr
            )
            
            # Calculate path metrics
            total_time = 0
            total_distance = 0
            total_cost = 0
            route_segments = []
            
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]
                edge_data = self.graph[current_node][next_node]
                
                total_time += edge_data['weight']
                total_distance += edge_data['distance']
                total_cost += edge_data['cost']
                
                route_segments.append({
                    'from': {
                        'id': current_node,
                        'name': self.node_data[current_node]['name'],
                        'coordinates': {
                            'latitude': self.node_data[current_node]['coords'][0],
                            'longitude': self.node_data[current_node]['coords'][1]
                        }
                    },
                    'to': {
                        'id': next_node,
                        'name': self.node_data[next_node]['name'],
                        'coordinates': {
                            'latitude': self.node_data[next_node]['coords'][0],
                            'longitude': self.node_data[next_node]['coords'][1]
                        }
                    },
                    'distance_km': round(edge_data['distance'], 2),
                    'time_minutes': round(edge_data['weight'], 0),
                    'cost': round(edge_data['cost'], 2),
                    'status': edge_data['status']
                })
            
            # Build complete node list
            route_nodes = []
            for node_id in path:
                route_nodes.append({
                    'id': node_id,
                    'name': self.node_data[node_id]['name'],
                    'type': self.node_data[node_id]['type'],
                    'coordinates': {
                        'latitude': self.node_data[node_id]['coords'][0],
                        'longitude': self.node_data[node_id]['coords'][1]
                    }
                })
            
            return {
                'status': 'success',
                'route': {
                    'nodes': route_nodes,
                    'segments': route_segments,
                    'summary': {
                        'total_distance_km': round(total_distance, 2),
                        'total_time_minutes': round(total_time, 0),
                        'total_cost': round(total_cost, 2),
                        'stops': len(path) - 2,  # Excluding origin and destination
                        'optimized_by': optimize_by
                    }
                }
            }
            
        except nx.NetworkXNoPath:
            return {
                'status': 'error',
                'error': 'No route available between these locations'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Route calculation failed: {str(e)}'
            }
    
    def get_all_routes_from_location(self, location_id: int) -> Dict:
        """
        Get all possible routes from a given location.
        
        Args:
            location_id: Starting location node ID
            
        Returns:
            Dictionary with all reachable destinations
        """
        if self.graph is None:
            self.build_graph()
        
        if location_id not in self.graph:
            return {
                'status': 'error',
                'error': 'Location not found'
            }
        
        # Get all nodes reachable from this location
        reachable = nx.single_source_shortest_path_length(
            self.graph,
            location_id,
            weight='weight'
        )
        
        destinations = []
        for dest_id, travel_time in reachable.items():
            if dest_id != location_id:  # Exclude source itself
                destinations.append({
                    'id': dest_id,
                    'name': self.node_data[dest_id]['name'],
                    'type': self.node_data[dest_id]['type'],
                    'estimated_time_minutes': round(travel_time, 0)
                })
        
        return {
            'status': 'success',
            'source': {
                'id': location_id,
                'name': self.node_data[location_id]['name']
            },
            'reachable_destinations': destinations,
            'count': len(destinations)
        }