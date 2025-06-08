from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import (
    init_database,
    insert_event,
    get_events,
    get_stats,
    clear_all_events,
)
from dashboard import get_dashboard_html
from models import Event
from websocket_manager import websocket_manager
import json

# Initialize FastAPI app
app = FastAPI(title="StreamCommerce Analytics", version="1.0.0")

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

        await websocket.send_text(
            json.dumps(
                {
                    "type": "initial_data",
                    "stats": stats,
                    "events": events_data["events"],
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
    await websocket_manager.send_stats_update(updated_stats)

    return {"status": "tracked", **result}


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
    Health check endpoint
    """
    return {"status": "healthy", "service": "StreamCommerce Analytics"}


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
