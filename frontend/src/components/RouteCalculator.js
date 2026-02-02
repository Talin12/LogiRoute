import React, { useState, useEffect } from 'react';
import { routeAPI } from '../services/api';

function RouteCalculator({ locations, onRouteCalculated }) {
  const [sourceId, setSourceId] = useState('');
  const [destId, setDestId] = useState('');
  const [optimizeBy, setOptimizeBy] = useState('time');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await routeAPI.calculate(
        parseInt(sourceId),
        parseInt(destId),
        optimizeBy
      );
      
      if (response.data.status === 'success') {
        onRouteCalculated(response.data.route);
      } else {
        setError(response.data.error || 'Route calculation failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to calculate route');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      <h2 style={{ marginTop: 0 }}>🗺️ Calculate Route</h2>
      
      <form onSubmit={handleCalculate}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            From:
          </label>
          <select
            value={sourceId}
            onChange={(e) => setSourceId(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
          >
            <option value="">Select origin</option>
            {locations?.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name} ({loc.node_type_display})
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            To:
          </label>
          <select
            value={destId}
            onChange={(e) => setDestId(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
          >
            <option value="">Select destination</option>
            {locations?.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name} ({loc.node_type_display})
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Optimize by:
          </label>
          <select
            value={optimizeBy}
            onChange={(e) => setOptimizeBy(e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
          >
            <option value="time">⏱️ Time (fastest)</option>
            <option value="distance">📏 Distance (shortest)</option>
            <option value="cost">💰 Cost (cheapest)</option>
          </select>
        </div>

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

        <button
          type="submit"
          disabled={loading || !sourceId || !destId}
          style={{
            width: '100%',
            padding: '12px',
            background: loading ? '#ccc' : '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '🔄 Calculating...' : '🚀 Calculate Route'}
        </button>
      </form>
    </div>
  );
}

export default RouteCalculator;
