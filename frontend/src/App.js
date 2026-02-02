import React, { useState, useEffect } from 'react';
import MapView from './components/MapView';
import RouteCalculator from './components/RouteCalculator';
import PackageTracker from './components/PackageTracker';
import { locationAPI } from './services/api';
import './App.css';

function App() {
  const [locations, setLocations] = useState([]);
  const [route, setRoute] = useState(null);
  const [packageLocation, setPackageLocation] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load locations on mount
  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      const response = await locationAPI.getAll();
      setLocations(response.data);
    } catch (error) {
      console.error('Failed to load locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRouteCalculated = (calculatedRoute) => {
    setRoute(calculatedRoute);
    setPackageLocation(null); // Clear package location when showing route
  };

  const handlePackageUpdate = (packageData) => {
    // Update package location on map
    if (packageData.current_coordinates) {
      setPackageLocation(packageData.current_coordinates);
    }
  };

  const clearRoute = () => {
    setRoute(null);
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '24px'
      }}>
        🚚 Loading LogiRoute...
      </div>
    );
  }

  return (
    <div className="App">
      <header style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <h1 style={{ margin: 0, fontSize: '32px' }}>
            🚚 LogiRoute - Intelligent Logistics
          </h1>
          <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>
            Graph-based route optimization powered by Dijkstra's Algorithm
          </p>
        </div>
      </header>

      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 20px'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '350px 1fr',
          gap: '20px',
          marginBottom: '20px'
        }}>
          {/* Left sidebar - Controls */}
          <div>
            <RouteCalculator
              locations={locations}
              onRouteCalculated={handleRouteCalculated}
            />
            
            <PackageTracker
              onPackageUpdate={handlePackageUpdate}
            />

            {/* Stats */}
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ marginTop: 0 }}>📊 Network Stats</h3>
              <div style={{ display: 'grid', gap: '10px' }}>
                <div style={{
                  padding: '10px',
                  background: '#f3f4f6',
                  borderRadius: '4px'
                }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2563eb' }}>
                    {locations.length}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>
                    Total Locations
                  </div>
                </div>
                
                <div style={{
                  padding: '10px',
                  background: '#f3f4f6',
                  borderRadius: '4px'
                }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                    {locations.filter(l => l.node_type === 'warehouse').length}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>
                    Warehouses
                  </div>
                </div>

                {route && (
                  <button
                    onClick={clearRoute}
                    style={{
                      padding: '10px',
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    Clear Route
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Right side - Map */}
          <div>
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
            }}>
              <MapView
                locations={locations}
                route={route}
                packageLocation={packageLocation}
              />
            </div>
          </div>
        </div>

        {/* Route Details */}
        {route && route.segments && (
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <h3 style={{ marginTop: 0 }}>🛣️ Route Details</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse'
              }}>
                <thead>
                  <tr style={{ background: '#f3f4f6' }}>
                    <th style={{ padding: '10px', textAlign: 'left' }}>From</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>To</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Distance</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Time</th>
                    <th style={{ padding: '10px', textAlign: 'right' }}>Cost</th>
                    <th style={{ padding: '10px', textAlign: 'center' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {route.segments.map((segment, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                      <td style={{ padding: '10px' }}>{segment.from.name}</td>
                      <td style={{ padding: '10px' }}>{segment.to.name}</td>
                      <td style={{ padding: '10px', textAlign: 'right' }}>
                        {segment.distance_km} km
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right' }}>
                        {segment.time_minutes} min
                      </td>
                      <td style={{ padding: '10px', textAlign: 'right' }}>
                        ₹{segment.cost}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'center' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          background: segment.status === 'active' ? '#dcfce7' : '#fef3c7',
                          color: segment.status === 'active' ? '#166534' : '#92400e'
                        }}>
                          {segment.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <footer style={{
        textAlign: 'center',
        padding: '20px',
        color: '#6b7280',
        marginTop: '40px'
      }}>
        <p>Built with React, Django, Celery & Dijkstra's Algorithm 🚀</p>
      </footer>
    </div>
  );
}

export default App;
