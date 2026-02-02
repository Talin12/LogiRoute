import React, { useState, useEffect, useRef } from 'react';
import { packageAPI, createWebSocket } from '../services/api';

function PackageTracker({ onPackageUpdate }) {
  const [trackingId, setTrackingId] = useState('PKG-F44B72572275');
  const [packageData, setPackageData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const ws = useRef(null);

  const connectWebSocket = (trackingId) => {
    if (ws.current) {
      ws.current.close();
    }

    const socket = createWebSocket(`/track/${trackingId}/`);
    
    socket.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message:', data);
      
      if (data.type === 'package_status' || data.type === 'package_update') {
        setPackageData(data.data);
        if (onPackageUpdate) {
          onPackageUpdate(data.data);
        }
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    ws.current = socket;
  };

  const handleTrack = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await packageAPI.track(trackingId);
      setPackageData(response.data.package);
      
      // Connect to WebSocket for real-time updates
      connectWebSocket(trackingId);
    } catch (err) {
      setError(err.response?.data?.error || 'Package not found');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const getStateColor = (state) => {
    const colors = {
      pending: '#f59e0b',
      in_transit: '#3b82f6',
      out_for_delivery: '#8b5cf6',
      delivered: '#10b981',
      cancelled: '#ef4444'
    };
    return colors[state] || '#6b7280';
  };

  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      <h2 style={{ marginTop: 0 }}>
        📦 Package Tracker
        {wsConnected && (
          <span style={{
            marginLeft: '10px',
            fontSize: '12px',
            color: '#10b981',
            fontWeight: 'normal'
          }}>
            🟢 Live
          </span>
        )}
      </h2>

      <form onSubmit={handleTrack}>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <input
            type="text"
            value={trackingId}
            onChange={(e) => setTrackingId(e.target.value)}
            placeholder="Enter tracking ID"
            required
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '10px 20px',
              background: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            {loading ? '🔍 Tracking...' : '🔍 Track'}
          </button>
        </div>
      </form>

      {error && (
        <div style={{
          background: '#fee',
          color: '#c00',
          padding: '10px',
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          {error}
        </div>
      )}

      {packageData && (
        <div style={{
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '15px',
          marginTop: '15px'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '15px'
          }}>
            <h3 style={{ margin: 0 }}>{packageData.tracking_id}</h3>
            <span style={{
              padding: '5px 12px',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 'bold',
              background: getStateColor(packageData.state) + '20',
              color: getStateColor(packageData.state)
            }}>
              {packageData.state_display}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <p style={{ margin: '5px 0', color: '#666', fontSize: '14px' }}>
                <strong>Origin:</strong>
              </p>
              <p style={{ margin: '5px 0' }}>{packageData.origin_name}</p>
            </div>

            <div>
              <p style={{ margin: '5px 0', color: '#666', fontSize: '14px' }}>
                <strong>Destination:</strong>
              </p>
              <p style={{ margin: '5px 0' }}>{packageData.destination_name}</p>
            </div>

            <div>
              <p style={{ margin: '5px 0', color: '#666', fontSize: '14px' }}>
                <strong>Current Location:</strong>
              </p>
              <p style={{ margin: '5px 0' }}>{packageData.current_location_name}</p>
            </div>

            <div>
              <p style={{ margin: '5px 0', color: '#666', fontSize: '14px' }}>
                <strong>Weight:</strong>
              </p>
              <p style={{ margin: '5px 0' }}>{packageData.weight_kg} kg</p>
            </div>
          </div>

          {packageData.description && (
            <div style={{ marginTop: '10px' }}>
              <p style={{ margin: '5px 0', color: '#666', fontSize: '14px' }}>
                <strong>Description:</strong>
              </p>
              <p style={{ margin: '5px 0' }}>{packageData.description}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PackageTracker;
