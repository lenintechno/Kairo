from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None


class ReminderOut(BaseModel):
    reminder_id: str
    text: str
    due_at: datetime


class RemindersDueResponse(BaseModel):
    reminders: List[ReminderOut]


class HealthResponse(BaseModel):
    status: str = "ok"