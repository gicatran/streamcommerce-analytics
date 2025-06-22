# StreamCommerce Analytics Platform

> Real-time e-commerce analytics platform with anomaly detection and user behavior analysis

[![Python 3.11+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/Real--time-WebSocket-red.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## 🎯 Project Overview

StreamCommerce is a production-ready analytics platform that processes e-commerce events in real-time, providing business insights through conversion funnels, user segmentation, and statistical anomaly detection.

## ✨ Key Features

### 📊 Real-Time Analytics Dashboard

-   **Live Event Tracking**: WebSocket-powered real-time event streaming
-   **Conversion Funnel Analysis**: Track user journey drop-off points
-   **User Intent Segmentation**: Classify users by purchase likelihood
-   **Statistical Anomaly Detection**: Identify traffic spikes, unusual purchases, and abnormal behavior

### 🛠 Technical Architecture

-   **Backend**: FastAPI with WebSocket support for real-time updates
-   **Database**: SQLite with optimized queries for analytics workloads
-   **Frontend**: Vanilla JavaScript with Chart.js for visualizations
-   **Real-time Processing**: Event-driven architecture with live data streaming

### 📈 Business Intelligence Features

-   **Conversion Rate Optimization**: Identify bottlenecks in user journey
-   **User Behavior Analytics**: Segment users by engagement patterns
-   **Anomaly Monitoring**: Real-time alerts for unusual system behavior
-   **Performance Metrics**: Track key business KPIs with live updates

## 🚀 Quick Start

### Prerequisites

-   Python 3.13+
-   Git

### Installation

```bash
# Clone repository
git clone https://github.com/gicatran/streamcommerce-analytics.git
cd streamcommerce-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

### Access Dashboard

Open http://localhost:8000 in your browser

## 📊 Demo & Testing

### Generate Sample Data

```bash
# Generate realistic user journeys
curl -X POST http://localhost:8000/demo/generate-traffic

# Generate anomalous behavior
curl -X POST http://localhost:8000/demo/generate-anomalies
```

### API Endpoints

```bash
# Analytics endpoints
GET /stats              # Business metrics
GET /funnel-analysis    # Conversion funnel data
GET /user-segmentation  # User intent classification
GET /anomalies         # Anomaly detection results

# Data endpoints
POST /track            # Track new events
GET /events           # Recent events
DELETE /events        # Clear all data
```

## 🏗 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Event Stream  │────│ Analytics Engine │────│   Dashboard     │
│                 │    │                  │    │                 │
│ • User Actions  │    │ • Funnel Analysis│    │ • Real-time UI  │
│ • Transactions  │    │ • Segmentation   │    │ • WebSocket     │
│ • Page Views    │    │ • Anomaly Det.   │    │ • Notifications │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  SQLite Store   │    │   WebSocket Hub  │    │   Chart.js      │
│                 │    │                  │    │                 │
│ • Events        │    │ • Live Updates   │    │ • Visualizations│
│ • User Sessions │    │ • Notifications  │    │ • Interactive   │
│ • Analytics     │    │ • Broadcasting   │    │ • Responsive    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔬 Technical Deep Dive

### Real-Time Event Processing

-   **WebSocket Architecture**: Bi-directional communication for instant updates
-   **Event-Driven Design**: Scalable architecture for high-throughput scenarios
-   **Statistical Analysis**: Real-time anomaly detection using moving averages and standard deviation

### Analytics Algorithms

```python
# Conversion Funnel Analysis
def calculate_funnel_conversion(events):
    """
    Tracks user progression through purchase funnel
    Returns conversion rates at each stage
    """

# User Intent Classification
def classify_user_intent(user_events):
    """
    Rule-based classification: browser/abandoner/converter
    Based on behavioral patterns and event sequences
    """

# Anomaly Detection
def detect_statistical_anomalies(time_series_data):
    """
    Statistical outlier detection using 2-sigma rule
    Identifies traffic spikes and unusual patterns
    """
```

### Data Models

```python
# Event Schema
{
  "event_type": "purchase|page_view|add_to_cart|user_signup|product_view",
  "user_id": "unique_identifier",
  "timestamp": "ISO_8601_datetime",
  "data": {
    "page": "/product/123",
    "amount": 99.99,
    "product_id": "prod_123"
  }
}
```

## 📊 Analytics Features

### Conversion Funnel Analysis

-   **Multi-step Funnel**: Track user progression through purchase journey
-   **Drop-off Identification**: Pinpoint where users abandon the process
-   **Real-time Conversion Rates**: Live updates as new data flows in

### User Segmentation

-   **High Intent**: Users likely to convert (added to cart + multiple interactions)
-   **Medium Intent**: Users showing interest (product views + engagement)
-   **Low Intent**: Browsers with minimal engagement
-   **Converted**: Users who completed purchases

### Anomaly Detection

-   **Traffic Spikes**: Detect unusual increases in event volume
-   **Purchase Anomalies**: Flag unusually high/low transaction amounts
-   **User Behavior**: Identify hyperactive or suspicious user patterns

## 🎨 Dashboard Features

### Real-Time Visualizations

-   **Live Event Stream**: See events flowing in real-time
-   **Conversion Funnel Chart**: Visual funnel with conversion percentages
-   **User Segmentation Cards**: Live user classification counts
-   **Anomaly Alert System**: Real-time notifications with severity levels

### Interactive Elements

-   **Test Event Buttons**: Generate sample events for demonstration
-   **Auto-refresh**: Dashboard updates automatically via WebSocket
-   **Responsive Design**: Works on desktop and mobile devices

## 🔧 Development

### Project Structure

```
streamcommerce-analytics/
├── src/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic data models
│   ├── database.py          # Data layer & analytics
│   ├── websocket_manager.py # Real-time communication
│   └── dashboard.py         # Frontend template loader
├── static/
│   ├── css/dashboard.css    # Styling
│   └── js/dashboard.js      # Frontend logic
├── templates/
│   └── dashboard.html       # Dashboard template
└── requirements.txt         # Dependencies
```

### Key Technologies

-   **FastAPI**: Modern Python web framework with automatic OpenAPI docs
-   **WebSockets**: Real-time bidirectional communication
-   **SQLite**: Lightweight database perfect for analytics workloads
-   **Chart.js**: Beautiful, responsive charts for data visualization

### Development Commands

```bash
# Run with hot reload
python src/main.py

# API Documentation
http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

## 📈 Business Impact

### Key Metrics Tracked

-   **Conversion Rate**: Overall and by funnel stage
-   **User Engagement**: Events per user, session patterns
-   **Anomaly Detection**: System health and unusual patterns
-   **Real-time Performance**: Live dashboard updates

### Business Value

-   **Optimize Conversion**: Identify and fix funnel bottlenecks
-   **User Understanding**: Segment users for targeted marketing
-   **System Monitoring**: Detect issues before they impact business
-   **Real-time Decisions**: Make data-driven decisions instantly

## 🎯 Use Cases

### E-commerce Optimization

-   Track where users drop off in purchase funnel
-   Identify high-value customers for VIP treatment
-   Detect fraudulent or unusual purchase patterns

### System Monitoring

-   Alert on traffic spikes that might indicate DDoS attacks
-   Monitor user behavior for abuse or bot activity
-   Track system performance in real-time

### Business Intelligence

-   Real-time dashboard for stakeholders
-   User behavior analysis for product improvements
-   A/B testing infrastructure for optimization

## 🚀 Deployment

### Production Considerations

-   **Database**: Migrate to PostgreSQL for production scale
-   **Caching**: Add Redis for improved performance
-   **Load Balancing**: Use nginx for high availability
-   **Monitoring**: Integrate with Prometheus/Grafana

## 🧪 Testing

### Sample Usage

```python
# Generate test events
import requests

# Track a purchase
requests.post('http://localhost:8000/track', json={
    'event_type': 'purchase',
    'user_id': 'user_123',
    'data': {'amount': 99.99, 'product': 'laptop'}
})

# Get analytics
response = requests.get('http://localhost:8000/stats')
print(response.json())
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
