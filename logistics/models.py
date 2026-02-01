from django.db import models
from django_fsm import FSMField, transition
from django.core.validators import MinValueValidator
import uuid


class LocationNode(models.Model):
    """Represents a location in the logistics network (warehouse, city, customer location)"""
    
    NODE_TYPES = [
        ('warehouse', 'Warehouse'),
        ('city', 'City Hub'),
        ('customer', 'Customer Location'),
    ]
    
    name = models.CharField(max_length=100)
    node_type = models.CharField(max_length=20, choices=NODE_TYPES)
    
    # For now, we'll use simple decimal fields for coordinates
    # We'll upgrade to PostGIS in Phase 2
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="Longitude coordinate"
    )
    
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['node_type']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_node_type_display()})"


class RouteEdge(models.Model):
    """Represents a connection/route between two locations"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Road Closed'),
        ('slow', 'Traffic Delay'),
    ]
    
    source = models.ForeignKey(
        LocationNode,
        on_delete=models.CASCADE,
        related_name='outgoing_routes'
    )
    destination = models.ForeignKey(
        LocationNode,
        on_delete=models.CASCADE,
        related_name='incoming_routes'
    )
    
    distance_km = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Distance in kilometers"
    )
    travel_time_minutes = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Estimated travel time in minutes"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Optional: cost per km for route optimization
    cost_per_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Cost per kilometer for this route"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['source', 'destination']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['source', 'destination']),
        ]
        ordering = ['source', 'destination']
    
    def __str__(self):
        return f"{self.source.name} → {self.destination.name} ({self.distance_km}km)"


class Package(models.Model):
    """Represents a package being shipped through the network"""
    
    tracking_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    
    # Locations
    origin = models.ForeignKey(
        LocationNode,
        on_delete=models.PROTECT,
        related_name='packages_originating'
    )
    current_location = models.ForeignKey(
        LocationNode,
        on_delete=models.PROTECT,
        related_name='packages_current'
    )
    destination = models.ForeignKey(
        LocationNode,
        on_delete=models.PROTECT,
        related_name='packages_destined'
    )
    
    # Package details
    weight_kg = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Package weight in kilograms"
    )
    description = models.TextField(blank=True)
    
    # FSM State Machine
    state = FSMField(
        default='pending',
        choices=[
            ('pending', 'Pending Pickup'),
            ('in_transit', 'In Transit'),
            ('out_for_delivery', 'Out for Delivery'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tracking_id']),
            models.Index(fields=['state']),
            models.Index(fields=['current_location']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            # Generate unique tracking ID
            self.tracking_id = f"PKG-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    # FSM Transitions
    @transition(field=state, source='pending', target='in_transit')
    def start_transit(self):
        """Start the package journey"""
        pass
    
    @transition(field=state, source='in_transit', target='in_transit')
    def move_to_location(self, new_location):
        """Move package to a new location during transit"""
        self.current_location = new_location
    
    @transition(field=state, source='in_transit', target='out_for_delivery')
    def start_delivery(self):
        """Package is out for final delivery"""
        pass
    
    @transition(field=state, source='out_for_delivery', target='delivered')
    def complete_delivery(self):
        """Mark package as delivered"""
        from django.utils import timezone
        self.delivered_at = timezone.now()
    
    @transition(field=state, source=['pending', 'in_transit'], target='cancelled')
    def cancel_package(self):
        """Cancel the package shipment"""
        pass
    
    def __str__(self):
        return f"{self.tracking_id} - {self.get_state_display()}"