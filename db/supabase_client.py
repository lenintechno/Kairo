from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


_supabase: Optional[Client] = None


def get_client() -> Client:
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


# ---------- Reminders ----------

def add_reminder(text: str, due_at: datetime) -> Dict[str, Any]:
    """Create a new reminder."""
    client = get_client()
    data = {
        "text": text,
        "due_at": due_at.isoformat(),
        "status": "pending",
    }
    result = client.table("reminders").insert(data).execute()
    return result.data[0] if result.data else {}


def list_reminders(filter: str = "all") -> List[Dict[str, Any]]:
    """Get reminders with optional filter: 'today', 'week', or 'all'."""
    client = get_client()
    query = client.table("reminders").select("*").eq("status", "pending")

    now = datetime.now()
    if filter == "today":
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.lte("due_at", end_of_day.isoformat())
    elif filter == "week":
        from datetime import timedelta
        end_of_week = now + timedelta(days=7)
        query = query.lte("due_at", end_of_week.isoformat())

    result = query.order("due_at", desc=False).execute()
    return result.data or []


def mark_reminder_done(reminder_id: str) -> Dict[str, Any]:
    """Mark a reminder as done."""
    client = get_client()
    result = (
        client.table("reminders")
        .update({"status": "done"})
        .eq("reminder_id", reminder_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def mark_reminder_notified(reminder_id: str) -> Dict[str, Any]:
    """Mark a reminder as notified."""
    client = get_client()
    result = (
        client.table("reminders")
        .update({"status": "notified"})
        .eq("reminder_id", reminder_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def get_due_pending_reminders() -> List[Dict[str, Any]]:
    """Get all pending reminders that are due now (for scheduler)."""
    client = get_client()
    now = datetime.now().isoformat()
    result = (
        client.table("reminders")
        .select("*")
        .eq("status", "pending")
        .lte("due_at", now)
        .execute()
    )
    return result.data or []


# ---------- Notes ----------

def add_note(content: str) -> Dict[str, Any]:
    """Create a new note."""
    client = get_client()
    data = {"content": content}
    result = client.table("notes").insert(data).execute()
    return result.data[0] if result.data else {}


def list_notes(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent notes."""
    client = get_client()
    result = (
        client.table("notes")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


# ---------- Conversation Log ----------

def log_message(role: str, content: str) -> Dict[str, Any]:
    """Log a user or assistant message."""
    client = get_client()
    data = {"role": role, "content": content}
    result = client.table("conversation_log").insert(data).execute()
    return result.data[0] if result.data else {}


def get_conversation_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent conversation history."""
    client = get_client()
    result = (
        client.table("conversation_log")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    # Return in chronological order
    return list(reversed(result.data or []))