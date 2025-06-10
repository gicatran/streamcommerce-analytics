import sqlite3
from models import Event
from typing import Dict, Any
from datetime import datetime, timezone
import json
import statistics

DB_FILE = "events.db"


def init_database():
    """
    Create the events table if it does not exist.
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            user_id TEXT,
            data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP           
        )               
        """
    )

    conn.commit()
    conn.close()


def insert_event(event: Event) -> Dict[str, Any]:
    """
    Insert a new event into the database
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    timestamp = datetime.now(timezone.utc).isoformat()
    data_json = json.dumps(event.data)

    cursor.execute(
        """
        INSERT INTO events (timestamp, event_type, user_id, data)
        VALUES (?, ?, ?, ?)
        """,
        (timestamp, event.event_type, event.user_id, data_json),
    )

    event_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    conn.close()

    return {"event_id": event_id, "total_events": total_events}


def get_events(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent events from the database
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, timestamp, event_type, user_id, data, created_at
        FROM events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()

    events = []
    for row in rows:
        events.append(
            {
                "id": row[0],
                "timestamp": row[1],
                "event_type": row[2],
                "user_id": row[3],
                "data": json.loads(row[4]) if row[4] else {},
                "created_at": row[5],
            }
        )

    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]

    conn.close()

    return {"events": events, "total": total}


def get_stats() -> Dict[str, Any]:
    """
    Get analytics statistics
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT event_type, COUNT(*) 
        FROM events
        GROUP BY event_type
        ORDER BY COUNT(*) DESC
        """
    )
    event_types = dict(cursor.fetchall())

    cursor.execute(
        "SELECT COUNT(DISTINCT user_id) FROM events WHERE user_id IS NOT NULL"
    )
    unique_users = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM events
        WHERE datetime(created_at) > datetime('now', '-1 hour')
        """
    )
    recent_events = cursor.fetchone()[0]

    conn.close()

    return {
        "total_events": total,
        "unique_users": unique_users,
        "event_last_hour": recent_events,
        "event_types": event_types,
    }


def clear_all_events() -> Dict[str, str]:
    """
    Clear all events from database
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM events")

    conn.commit()
    conn.close()


def get_funnel_analysis():
    """
    Calculate conversion funnel with percentages
    """

    result = get_events(200)
    events = result["events"]

    user_journeys = {}
    for event in events:
        user_id = event.get("user_id", "anonymous")

        if user_id not in user_journeys:
            user_journeys[user_id] = []
        user_journeys[user_id].append(event["event_type"])

    funnel_counts = {
        "page_view": 0,
        "product_view": 0,
        "add_to_cart": 0,
        "user_signup": 0,
        "purchase": 0,
    }

    for user_id, events_list in user_journeys.items():
        if "page_view" in events_list:
            funnel_counts["page_view"] += 1
        if "product_view" in events_list:
            funnel_counts["product_view"] += 1
        if "add_to_cart" in events_list:
            funnel_counts["add_to_cart"] += 1
        if "user_signup" in events_list:
            funnel_counts["user_signup"] += 1
        if "purchase" in events_list:
            funnel_counts["purchase"] += 1

    total_users = funnel_counts["page_view"]
    conversion_rates = {}

    if total_users > 0:
        conversion_rates = {
            "page_view": 100.0,
            "product_view": round(
                (funnel_counts["product_view"] / total_users) * 100, 1
            ),
            "add_to_cart": round((funnel_counts["add_to_cart"] / total_users) * 100, 1),
            "user_signup": round((funnel_counts["user_signup"] / total_users) * 100, 1),
            "purchase": round((funnel_counts["purchase"] / total_users) * 100, 1),
        }

    return {
        "funnel_counts": funnel_counts,
        "conversion_rates": conversion_rates,
        "total_users": total_users,
    }


def classify_user_intent(user_events):
    """
    Classify user intent based on behavior patterns
    """

    event_types = [e["event_type"] for e in user_events]
    total_events = len(user_events)

    if "purchase" in event_types:
        return "converted"

    if "add_to_cart" in event_types:
        if total_events >= 5:
            return "high_intent"
        else:
            return "medium_intent"

    if "product_view" in event_types:
        if total_events >= 3:
            return "medium_intent"
        else:
            return "low_intent"

    return "low_intent"


def get_user_segmentation():
    """
    Get real-time user intent segmentation
    """

    result = get_events(200)
    events = result["events"]

    user_journeys = {}
    for event in events:
        user_id = event.get("user_id", "anonymous")

        if user_id not in user_journeys:
            user_journeys[user_id] = []

        user_journeys[user_id].append(event)

    segmentation = {
        "high_intent": [],
        "medium_intent": [],
        "low_intent": [],
        "converted": [],
    }

    for user_id, user_events in user_journeys.items():
        intent = classify_user_intent(user_events)
        segmentation[intent].append(
            {
                "user_id": user_id,
                "total_events": len(user_events),
                "last_event": user_events[-1]["event_type"] if user_events else None,
            }
        )

    return segmentation


def detect_anomalies():
    """
    Detect statistical anomalies in recent event patterns
    """

    result = get_events(100)
    events = result["events"]

    if len(events) < 10:
        return {"anomalies": [], "message": "Insufficient data for anomaly detection"}

    anomalies = []

    time_windows = {}
    for event in events:
        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        window = timestamp.replace(
            minute=(timestamp.minute // 5) * 5, second=0, microsecond=0
        )
        window_key = window.isoformat()

        if window_key not in time_windows:
            time_windows[window_key] = 0
        time_windows[window_key] += 1

    event_counts = list(time_windows.values())
    if len(event_counts) >= 3:
        avg_rate = statistics.mean(event_counts)
        std_rate = statistics.stdev(event_counts) if len(event_counts) > 1 else 0
        current_rate = event_counts[-1]

        if std_rate > 0 and current_rate > avg_rate + (2 * std_rate):
            anomalies.append(
                {
                    "type": "traffic_spike",
                    "severity": "high",
                    "message": f"Traffic spike detected: {current_rate} events in 5 min (avg: {avg_rate:.1f})",
                    "current_value": current_rate,
                    "expected_range": f"{avg_rate - std_rate:.1f} - {avg_rate + std_rate:.1f}",
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    purchase_events = [e for e in events if e["event_type"] == "purchase"]
    if len(purchase_events) >= 5:
        amounts = []
        for event in purchase_events:
            amount = event.get("data", {}).get("amount", 0)
            if amount > 0:
                amounts.append(amount)

        if len(amounts) >= 5:
            avg_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts)

            recent_purchases = purchase_events[-3:]
            for purchase in recent_purchases:
                amount = purchase.get("data", {}).get("amount", 0)
                if amount > avg_amount + (2 * std_amount):
                    anomalies.append(
                        {
                            "type": "unsual_purchase",
                            "severity": "medium",
                            "message": f"Unusual high purchase: ${amount} (avg: ${avg_amount:.2f})",
                            "current_value": amount,
                            "expected_range": f"${avg_amount - std_amount:.2f} - ${avg_amount + std_amount:.2f}",
                            "user_id": purchase.get("user_id"),
                            "detected_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )

    user_activity = {}
    for event in events:
        user_id = event.get("user_id", "anonymous")
        if user_id not in user_activity:
            user_activity[user_id] = 0
        user_activity[user_id] += 1

    activity_counts = list(user_activity.values())
    if len(activity_counts) >= 5:
        avg_activity = statistics.mean(activity_counts)
        std_activity = statistics.stdev(activity_counts)

        for user_id, activity_count in user_activity.items():
            if activity_count > avg_activity + (2 * std_activity):
                anomalies.append(
                    {
                        "type": "hyperactive_user",
                        "severity": "low",
                        "message": f"User {user_id} has unsual activity: {activity_count} events (avg: {avg_activity:.1f})",
                        "current_value": activity_count,
                        "expected_range": f"{avg_activity - std_activity:.1f} - {avg_activity + std_activity:.1f}",
                        "user_id": user_id,
                        "detected_at": datetime.now(timezone.utc).isoformat(),
                    }
                )

    return {
        "anomalies": anomalies,
        "total_anomalies": len(anomalies),
        "analysis_period": "last 100 events",
        "detection_types": ["traffic_spike", "unusual_purchase", "hyperactive_user"],
    }


# Initialize the database on startup
init_database()
