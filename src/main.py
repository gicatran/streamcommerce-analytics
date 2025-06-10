"""
StreamCommerce Analytics Platform

Real-time e-commerce analytics with conversion tracking,
user segmentation, and anomaly detection.

Author: Gica Tran
Date: 2025
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import (
    init_database,
    insert_event,
    get_events,
    get_stats,
    clear_all_events,
    get_funnel_analysis,
    get_user_segmentation,
    detect_anomalies,
)
from dashboard import get_dashboard_html
from models import Event
from websocket_manager import websocket_manager
import json
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="StreamCommerce Analytics Platform",
    description="Real-time e-commerce analytics with anomaly detection",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database on startup
init_database()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    """

    await websocket_manager.connect(websocket)

    try:
        stats = get_stats()
        events_data = get_events(10)
        funnel_data = get_funnel_analysis()
        segmentation_data = get_user_segmentation()
        anomaly_data = detect_anomalies()

        await websocket.send_text(
            json.dumps(
                {
                    "type": "initial_data",
                    "stats": stats,
                    "events": events_data["events"],
                    "funnel": funnel_data,
                    "segmentation": segmentation_data,
                    "anomalies": anomaly_data,
                }
            )
        )

        while True:
            # Wait for any message from client (keepalive)
            try:
                await websocket.receive_text()
            except:
                break
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    """
    Main dashboard page
    """

    return get_dashboard_html()


@app.post("/track")
async def track_event(event: Event):
    """
    Track a new event - now with real-time updates
    """

    try:
        logger.info(f"Tracking event: {event.event_type} for user {event.user_id}")

        newEvent = Event(
            event_type=event.event_type,
            user_id=event.user_id,
            data=event.data,
        )

        result = insert_event(newEvent)

        event_data = {
            "id": result["event_id"],
            "event_type": newEvent.event_type,
            "user_id": newEvent.user_id,
            "data": newEvent.data,
            "timestamp": "just now",
        }

        await websocket_manager.send_event_update(event_data)

        updated_stats = get_stats()
        funnel_data = get_funnel_analysis()
        segmentation_data = get_user_segmentation()
        anomaly_data = detect_anomalies()

        await websocket_manager.send_stats_update(updated_stats)
        await websocket_manager.send_to_all(
            {"type": "funnel_update", "data": funnel_data}
        )
        await websocket_manager.send_to_all(
            {"type": "segmentation_update", "data": segmentation_data}
        )
        await websocket_manager.send_to_all(
            {"type": "anomaly_update", "data": anomaly_data}
        )

        logger.info(f"Successfully tracked event {result['event_id']}")
        return {"status": "tracked", **result}
    except Exception as e:
        logger.error(f"Error tracking event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track event")


@app.get("/events")
def list_events(limit: int = 10):
    """
    Get recent events
    """

    result = get_events(limit)

    return {
        **result,
        "showing": f"last {len(result['events'])} events",
    }


@app.get("/stats")
def analytics_stats():
    """
    Get analytics statistics
    """

    return get_stats()


@app.delete("/events")
async def clear_events():
    """
    Clear all events - useful for testing.
    """

    clear_all_events()

    await websocket_manager.send_stats_update(
        {
            "total_events": 0,
            "unique_users": 0,
            "event_last_hour": 0,
            "event_types": {},
        }
    )

    return {
        "status": "cleared",
        "message": "All events deleted",
    }


@app.get("/health")
def health_check():
    """
    Production health check endpoint
    """

    return {
        "status": "healthy",
        "service": "StreamCommerce Analytics",
        "version": "1.0.0",
        "features": [
            "real-time-analytics",
            "conversion-funnels",
            "user-segmentation",
            "anomaly-detection",
        ],
    }


@app.post("/demo/generate-traffic")
async def generate_demo_traffic():
    """
    Generate some demo traffic for testing real-time updates
    """

    import random
    import asyncio

    # Create 3 realistic user journeys
    for i in range(3):
        user_id = f"demo_user_{random.randint(100, 999)}"

        user_type = random.choice(["browser", "anbandoner", "converter"])

        if user_type == "browser":
            await track_event(
                Event(event_type="page_view", user_id=user_id, data={"page": "/home"})
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="product_view",
                    user_id=user_id,
                    data={"product": "laptop", "price": 999},
                )
            )
        elif user_type == "anbandoner":
            await track_event(
                Event(event_type="page_view", user_id=user_id, data={"page": "/home"})
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="product_view",
                    user_id=user_id,
                    data={"product": "laptop", "price": 999},
                )
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="add_to_cart",
                    user_id=user_id,
                    data={"product": "laptop", "quantity": 1},
                )
            )
        elif user_type == "converter":
            await track_event(
                Event(event_type="page_view", user_id=user_id, data={"page": "/home"})
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="product_view",
                    user_id=user_id,
                    data={"product": "laptop", "price": 999},
                )
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="add_to_cart",
                    user_id=user_id,
                    data={"product": "laptop", "quantity": 1},
                )
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="user_signup", user_id=user_id, data={"method": "email"}
                )
            )
            await asyncio.sleep(0.3)
            await track_event(
                Event(
                    event_type="purchase",
                    user_id=user_id,
                    data={"amount": 999, "payment": "card"},
                )
            )

    return {
        "status": "Realistic demo traffic generated",
        "users_created": 3,
    }


@app.get("/user-activity")
def get_user_activity():
    """
    Show recent user journeys
    """

    result = get_events(50)
    events = result["events"]

    user_journeys = {}
    for event in events:
        user_id = event.get("user_id", "anonymous")

        if user_id not in user_journeys:
            user_journeys[user_id] = []
        user_journeys[user_id].append(event)

    for user_id in user_journeys:
        user_journeys[user_id].sort(key=lambda x: x["timestamp"])

    return {"user_journeys": user_journeys}


@app.get("/funnel-analysis")
def funnel_analysis():
    """
    Get conversion funnel analysis
    """

    return get_funnel_analysis()


@app.get("/user-patterns")
def analyze_user_patterns():
    """
    Analyze user behavior patterns to understand intent signals
    """

    result = get_events(200)
    events = result["events"]

    user_journeys = {}
    for event in events:
        user_id = event.get("user_id", "anonymous")

        if user_id not in user_journeys:
            user_journeys[user_id] = []

        user_journeys[user_id].append(
            {
                "event_type": event["event_type"],
                "timestamp": event["timestamp"],
                "data": event["data"],
            }
        )

    user_analysis = {}
    for user_id, events_list in user_journeys.items():
        events_list.sort(key=lambda x: x["timestamp"])

        event_types = [e["event_type"] for e in events_list]

        analysis = {
            "total_events": len(events_list),
            "event_sequence": event_types,
            "converted": "purchase" in event_types,
            "added_to_cart": "add_to_cart" in event_types,
            "viewed_products": "product_view" in event_types,
            "signup": "user_signup" in event_types,
        }

        user_analysis[user_id] = analysis

    return {"user_patterns": user_analysis}


@app.get("/user-segmentation")
def user_segmentation():
    """
    Get real-time user intent segmentation
    """

    return get_user_segmentation()


@app.get("/anomalies")
def get_anomalies():
    """
    Get real-time anomaly detection results
    """

    return detect_anomalies()


@app.post("/demo/generate-anomalies")
async def generate_anomalies():
    """Generate anomalous behavior to test detection"""
    import random
    import asyncio

    # 1. Create traffic spike - send many events quickly
    for i in range(15):  # Send 15 events rapidly
        event = Event(
            event_type="page_view", user_id=f"spike_user_{i}", data={"page": "/home"}
        )
        await track_event(event)
        await asyncio.sleep(0.1)  # Very fast

    # 2. Create unusual purchase amounts
    for i in range(3):
        unusual_amount = random.randint(5000, 10000)  # Much higher than normal $999
        event = Event(
            event_type="purchase",
            user_id=f"whale_user_{i}",
            data={"amount": unusual_amount, "payment": "card"},
        )
        await track_event(event)
        await asyncio.sleep(0.2)

    # 3. Create hyperactive user
    hyperactive_user = "spam_user_999"
    for i in range(12):  # One user does lots of actions
        event_types = ["page_view", "product_view", "add_to_cart"]
        event = Event(
            event_type=random.choice(event_types),
            user_id=hyperactive_user,
            data={"action": f"spam_action_{i}"},
        )
        await track_event(event)
        await asyncio.sleep(0.1)

    return {"status": "Anomalies generated", "message": "Check /anomalies endpoint"}


# API v1 routes
@app.get("/api/v1/stats")
def get_stats_v1():
    """Get analytics statistics - API v1"""
    try:
        return get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.get("/api/v1/funnel")
def get_funnel_v1():
    """Get conversion funnel analysis - API v1"""
    try:
        return get_funnel_analysis()
    except Exception as e:
        logger.error(f"Error getting funnel: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get funnel analysis")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
