import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers not showing
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom icons for different node types
const warehouseIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const cityIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const customerIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Component to fit bounds when route changes
function FitBounds({ positions }) {
  const map = useMap();
  
  useEffect(() => {
    if (positions && positions.length > 0) {
      const bounds = L.latLngBounds(positions);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [positions, map]);
  
  return null;
}

function MapView({ locations, route, packageLocation }) {
  const getIcon = (nodeType) => {
    switch (nodeType) {
      case 'warehouse':
        return warehouseIcon;
      case 'city':
        return cityIcon;
      case 'customer':
        return customerIcon;
      default:
        return new L.Icon.Default();
    }
  };

  // Extract route coordinates for polyline
  const routePositions = route?.nodes?.map(node => [
    node.coordinates.latitude,
    node.coordinates.longitude
  ]) || [];

  // Default center (India)
  const defaultCenter = [20.5937, 78.9629];
  const defaultZoom = 5;

  return (
    <div style={{ height: '600px', width: '100%', position: 'relative' }}>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Location markers */}
        {locations?.map((location) => (
          <Marker
            key={location.id}
            position={[location.coordinates.latitude, location.coordinates.longitude]}
            icon={getIcon(location.node_type)}
          >
            <Popup>
              <div>
                <h3 style={{ margin: '0 0 10px 0' }}>{location.name}</h3>
                <p style={{ margin: '5px 0' }}>
                  <strong>Type:</strong> {location.node_type_display}
                </p>
                <p style={{ margin: '5px 0' }}>
                  <strong>Address:</strong> {location.address || 'N/A'}
                </p>
                <p style={{ margin: '5px 0', fontSize: '12px', color: '#666' }}>
                  {location.coordinates.latitude.toFixed(4)}, {location.coordinates.longitude.toFixed(4)}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Route polyline */}
        {route && routePositions.length > 0 && (
          <>
            <Polyline
              positions={routePositions}
              color="#2563eb"
              weight={4}
              opacity={0.7}
            />
            <FitBounds positions={routePositions} />
          </>
        )}

        {/* Package current location (if provided) */}
        {packageLocation && (
          <Marker
            position={[packageLocation.latitude, packageLocation.longitude]}
            icon={new L.Icon({
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41]
            })}
          >
            <Popup>
              <div>
                <h3 style={{ margin: '0' }}>📦 Package Location</h3>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Route info overlay */}
      {route && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'white',
          padding: '15px',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          zIndex: 1000,
          minWidth: '250px'
        }}>
          <h4 style={{ margin: '0 0 10px 0' }}>📍 Route Summary</h4>
          <p style={{ margin: '5px 0' }}>
            <strong>Distance:</strong> {route.summary.total_distance_km} km
          </p>
          <p style={{ margin: '5px 0' }}>
            <strong>Time:</strong> {Math.floor(route.summary.total_time_minutes / 60)}h {route.summary.total_time_minutes % 60}m
          </p>
          <p style={{ margin: '5px 0' }}>
            <strong>Cost:</strong> ₹{route.summary.total_cost.toFixed(2)}
          </p>
          <p style={{ margin: '5px 0' }}>
            <strong>Stops:</strong> {route.summary.stops}
          </p>
        </div>
      )}
    </div>
  );
}

export default MapView;
