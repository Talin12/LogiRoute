import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Package


class PackageTrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time package tracking.
    
    Connect to: ws://localhost:8000/ws/track/{tracking_id}/
    """
    
    async def connect(self):
        self.tracking_id = self.scope['url_route']['kwargs']['tracking_id']
        self.room_group_name = f'package_{self.tracking_id}'
        
        # Join tracking room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial package data
        package_data = await self.get_package_data()
        if package_data:
            await self.send(text_data=json.dumps({
                'type': 'package_status',
                'data': package_data
            }))
    
    async def disconnect(self, close_code):
        # Leave tracking room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'request_update':
            # Client requested current status
            package_data = await self.get_package_data()
            if package_data:
                await self.send(text_data=json.dumps({
                    'type': 'package_status',
                    'data': package_data
                }))
    
    async def package_update(self, event):
        """Receive message from room group"""
        await self.send(text_data=json.dumps({
            'type': 'package_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_package_data(self):
        """Fetch package data from database"""
        try:
            package = Package.objects.select_related(
                'origin', 'current_location', 'destination'
            ).get(tracking_id=self.tracking_id)
            
            return {
                'tracking_id': package.tracking_id,
                'state': package.state,
                'state_display': package.get_state_display(),
                'origin': package.origin.name,
                'current_location': package.current_location.name,
                'destination': package.destination.name,
                'current_coordinates': {
                    'latitude': float(package.current_location.latitude),
                    'longitude': float(package.current_location.longitude)
                },
                'weight_kg': package.weight_kg,
                'description': package.description,
                'created_at': package.created_at.isoformat(),
                'updated_at': package.updated_at.isoformat()
            }
        except Package.DoesNotExist:
            return None


class RouteVisualizationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time route visualization updates.
    
    Connect to: ws://localhost:8000/ws/routes/
    """
    
    async def connect(self):
        self.room_group_name = 'route_updates'
        
        # Join route updates room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def route_update(self, event):
        """Send route update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'route_update',
            'data': event['data']
        }))