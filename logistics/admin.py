from django.contrib import admin
from .models import LocationNode, RouteEdge, Package


@admin.register(LocationNode)
class LocationNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'node_type', 'latitude', 'longitude', 'is_active', 'created_at']
    list_filter = ['node_type', 'is_active']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'node_type', 'is_active')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RouteEdge)
class RouteEdgeAdmin(admin.ModelAdmin):
    list_display = ['source', 'destination', 'distance_km', 'travel_time_minutes', 'status', 'cost_per_km']
    list_filter = ['status']
    search_fields = ['source__name', 'destination__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Route Information', {
            'fields': ('source', 'destination', 'status')
        }),
        ('Metrics', {
            'fields': ('distance_km', 'travel_time_minutes', 'cost_per_km')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['tracking_id', 'state', 'origin', 'current_location', 'destination', 'weight_kg', 'created_at']
    list_filter = ['state', 'created_at']
    search_fields = ['tracking_id', 'description']
    readonly_fields = ['tracking_id', 'created_at', 'updated_at', 'delivered_at']
    
    fieldsets = (
        ('Tracking', {
            'fields': ('tracking_id', 'state')
        }),
        ('Locations', {
            'fields': ('origin', 'current_location', 'destination')
        }),
        ('Package Details', {
            'fields': ('weight_kg', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make state readonly after creation to enforce FSM transitions
        if obj:  # Editing existing object
            return self.readonly_fields + ('state',)
        return self.readonly_fields