# 🚚 LogiRoute - Intelligent Logistics Routing System

A Django-based logistics management system that uses graph algorithms to calculate optimal delivery routes.

## 🎯 Features

### Phase 1 (Current) ✅
- **Graph-Based Routing**: Dijkstra's algorithm for shortest path calculation
- **Multi-Criteria Optimization**: Route optimization by time, distance, or cost
- **State Machine Workflow**: Package tracking with FSM (django-fsm)
- **REST API**: Complete CRUD operations for locations, routes, and packages
- **Real-time Status**: Dynamic route calculation based on road conditions
- **Admin Interface**: Full Django admin for data management

### Tech Stack
- **Backend**: Django 5.0, Django REST Framework
- **Graph Engine**: NetworkX (Dijkstra's Algorithm)
- **State Management**: django-fsm
- **Database**: SQLite (Phase 1) → PostgreSQL + PostGIS (Phase 2)
- **API**: RESTful with JSON responses

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd LogiRoute
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Load sample data** (optional)
```bash
python manage.py shell < scripts/load_sample_data.py
```

8. **Start the server**
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/admin/

## 📡 API Endpoints

### Locations
```bash
# List all locations
GET /api/locations/

# Get specific location
GET /api/locations/{id}/

# Create new location
POST /api/locations/
{
  "name": "Mumbai Warehouse",
  "node_type": "warehouse",
  "latitude": 19.076090,
  "longitude": 72.877426,
  "address": "Andheri East, Mumbai"
}
```

### Route Calculation
```bash
# Calculate optimal route
POST /api/calculate-route/
{
  "source_id": 1,
  "destination_id": 5,
  "optimize_by": "time"  # Options: time, distance, cost
}

# Response:
{
  "status": "success",
  "route": {
    "nodes": [...],
    "segments": [...],
    "summary": {
      "total_distance_km": 1015.0,
      "total_time_minutes": 945,
      "total_cost": 5025.0,
      "stops": 2
    }
  }
}
```

### Package Tracking
```bash
# Track package
GET /api/track/{tracking_id}/

# List all packages
GET /api/packages/

# Update package state
POST /api/packages/{id}/transition/
{
  "action": "start_transit"
}
```

## 🏗️ Architecture

### Model Layer (The Brain)
- **LocationNode**: Warehouses, cities, customer locations with coordinates
- **RouteEdge**: Connections between locations with distance, time, cost
- **Package**: Shipments with FSM state tracking

### Service Layer (The Engine)
- **RouteCalculator**: Graph-based pathfinding using Dijkstra's algorithm
- Handles dynamic edge weights based on route status
- Supports multiple optimization criteria

### View Layer (The Controller)
- RESTful API endpoints
- Request validation with DRF serializers
- Business logic orchestration

## 🧪 Testing
```bash
# Test route calculation
curl -X POST http://127.0.0.1:8000/api/calculate-route/ \
  -H "Content-Type: application/json" \
  -d '{"source_id": 1, "destination_id": 5}'

# Test package tracking
curl http://127.0.0.1:8000/api/track/PKG-XXXXXXXXXXXX/
```

## 📊 Project Structure
```
LogiRoute/
├── config/              # Django settings
├── logistics/           # Main application
│   ├── models.py       # Data models
│   ├── views.py        # API endpoints
│   ├── serializers.py  # DRF serializers
│   ├── services/       # Business logic
│   │   └── graph_engine.py  # Dijkstra's implementation
│   └── admin.py        # Admin interface
├── manage.py
└── requirements.txt
```

## 🔮 Roadmap

### Phase 2 (Upcoming)
- [ ] PostgreSQL + PostGIS for geospatial queries
- [ ] Celery for async route calculation
- [ ] Redis for caching
- [ ] Django Channels for WebSocket real-time tracking

### Phase 3 (Future)
- [ ] React.js frontend with interactive maps (Leaflet.js/Mapbox)
- [ ] A* algorithm for faster routing
- [ ] Multi-vehicle routing optimization
- [ ] Load balancing across warehouses

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Graph algorithms (Dijkstra's) in production
- ✅ Clean architecture (MVC pattern)
- ✅ State machines for workflow management
- ✅ RESTful API design
- ✅ Geospatial data modeling
- ✅ Algorithm optimization strategies

## 📝 License

MIT License

## 👨‍💻 Author

Built as a learning project to demonstrate advanced Django architecture and computer science algorithms in a real-world logistics context.
