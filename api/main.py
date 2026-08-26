from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from api.schemas import (
    ChatRequest,
    ChatResponse,
    RemindersDueResponse,
    ReminderOut,
    HealthResponse,
)
from agent.assistant import run_assistant
from db.supabase_client import get_due_pending_reminders
from scheduler.reminder_checker import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(title="Kairo API", lifespan=lifespan)


# Mount static files for the web UI
web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
app.mount("/static", StaticFiles(directory=web_dir), name="static")


@app.get("/", response_class=FileResponse)
async def root():
    """Serve the main UI."""
    return FileResponse(os.path.join(web_dir, "index.html"))


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the assistant."""
    reply, tool_used = await run_assistant(request.message)
    return ChatResponse(reply=reply, tool_used=tool_used)


@app.get("/reminders/due", response_model=RemindersDueResponse)
async def reminders_due():
    """Get due reminders for proactive notification."""
    due = get_due_pending_reminders()
    reminders = [
        ReminderOut(
            reminder_id=r["reminder_id"],
            text=r["text"],
            due_at=r["due_at"],
        )
        for r in due
    ]
    return RemindersDueResponse(reminders=reminders)