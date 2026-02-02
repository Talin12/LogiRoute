import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';
const WS_BASE_URL = 'ws://127.0.0.1:8000/ws';

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const locationAPI = {
  getAll: () => api.get('/locations/'),
  getById: (id) => api.get(`/locations/${id}/`),
  create: (data) => api.post('/locations/', data),
};

export const routeAPI = {
  getAll: () => api.get('/routes/'),
  calculate: (sourceId, destId, optimizeBy = 'time') =>
    api.post('/calculate-route/', {
      source_id: sourceId,
      destination_id: destId,
      optimize_by: optimizeBy,
    }),
  calculateAsync: (sourceId, destId, optimizeBy = 'time') =>
    api.post('/calculate-route-async/', {
      source_id: sourceId,
      destination_id: destId,
      optimize_by: optimizeBy,
    }),
  getTaskStatus: (taskId) => api.get(`/task-status/${taskId}/`),
};

export const packageAPI = {
  getAll: () => api.get('/packages/'),
  getById: (id) => api.get(`/packages/${id}/`),
  track: (trackingId) => api.get(`/track/${trackingId}/`),
  transition: (id, action, newLocationId = null) =>
    api.post(`/packages/${id}/transition/`, {
      action,
      new_location_id: newLocationId,
    }),
};

// WebSocket helper
export const createWebSocket = (path) => {
  return new WebSocket(`${WS_BASE_URL}${path}`);
};

export default api;
