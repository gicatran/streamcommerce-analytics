from typing import List
from fastapi import WebSocket
import json


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_to_all(self, message: dict):
        """
        Send a message to all connected clients.
        """

        if not self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)

    async def send_event_update(self, event_data: dict):
        """
        Send real-time event update to all clients
        """

        await self.send_to_all({"type": "new_event", "data": event_data})

    async def send_stats_update(self, stats_data: dict):
        """
        Send updated statistics to all clients
        """

        await self.send_to_all({"type": "stats_update", "data": stats_data})


websocket_manager = WebSocketManager()
