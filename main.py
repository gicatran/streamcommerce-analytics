from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone

app = FastAPI()

events = []


class Event(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    data: Dict[str, Any] = {}


@app.get("/")
def root():
    return {"message": "StreamCommerce Analytics", "events_stored": len(events)}


@app.post("/track")
def track_event(event: Event):
    event_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event.event_type,
        "user_id": event.user_id,
        "data": event.data,
    }
    events.append(event_data)
    return {"status": "tracked", "total_events": len(events)}


@app.get("/events")
def get_events():
    return {"events": events[-10:], "total": len(events)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
