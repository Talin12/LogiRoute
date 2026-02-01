from rest_framework import serializers
from .models import LocationNode, RouteEdge, Package


class LocationNodeSerializer(serializers.ModelSerializer):
    """Serializer for LocationNode model"""
    
    node_type_display = serializers.CharField(source='get_node_type_display', read_only=True)
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = LocationNode
        fields = [
            'id', 'name', 'node_type', 'node_type_display',
            'latitude', 'longitude', 'coordinates',
            'address', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_coordinates(self, obj):
        return {
            'latitude': float(obj.latitude),
            'longitude': float(obj.longitude)
        }


class RouteEdgeSerializer(serializers.ModelSerializer):
    """Serializer for RouteEdge model"""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RouteEdge
        fields = [
            'id', 'source', 'source_name', 'destination', 'destination_name',
            'distance_km', 'travel_time_minutes', 'cost_per_km',
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PackageSerializer(serializers.ModelSerializer):
    """Serializer for Package model"""
    
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    current_location_name = serializers.CharField(source='current_location.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'tracking_id', 'state', 'state_display',
            'origin', 'origin_name',
            'current_location', 'current_location_name',
            'destination', 'destination_name',
            'weight_kg', 'description',
            'created_at', 'updated_at', 'delivered_at'
        ]
        read_only_fields = ['tracking_id', 'created_at', 'updated_at', 'delivered_at']


class RouteCalculationRequestSerializer(serializers.Serializer):
    """Serializer for route calculation requests"""
    
    source_id = serializers.IntegerField(required=True)
    destination_id = serializers.IntegerField(required=True)
    optimize_by = serializers.ChoiceField(
        choices=['time', 'distance', 'cost'],
        default='time',
        required=False
    )


class PackageStateTransitionSerializer(serializers.Serializer):
    """Serializer for package state transitions"""
    
    action = serializers.ChoiceField(
        choices=['start_transit', 'move_to_location', 'start_delivery', 'complete_delivery', 'cancel'],
        required=True
    )
    new_location_id = serializers.IntegerField(required=False, allow_null=True)