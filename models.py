from pydantic import BaseModel
from typing import Optional, Dict, Any


class Event(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    data: Dict[str, Any] = {}
