from db.supabase_client import (
    add_reminder,
    list_reminders,
    mark_reminder_done,
    add_note,
    list_notes,
)
from datetime import datetime
from typing import Dict, Any
import json


async def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name with the given arguments. Returns the tool result."""
    try:
        if name == "add_reminder":
            text = arguments.get("text")
            due_at_str = arguments.get("due_at")
            if not text or not due_at_str:
                return {"error": "Missing required arguments: text and due_at"}
            due_at = datetime.fromisoformat(due_at_str.replace("Z", "+00:00"))
            result = add_reminder(text, due_at)
            return result

        elif name == "list_reminders":
            filter_val = arguments.get("filter", "all")
            result = list_reminders(filter_val)
            return {"reminders": result}

        elif name == "mark_reminder_done":
            reminder_id = arguments.get("reminder_id")
            if not reminder_id:
                return {"error": "Missing required argument: reminder_id"}
            result = mark_reminder_done(reminder_id)
            return result

        elif name == "add_note":
            content = arguments.get("content")
            if not content:
                return {"error": "Missing required argument: content"}
            result = add_note(content)
            return result

        elif name == "list_notes":
            limit = arguments.get("limit", 10)
            result = list_notes(limit)
            return {"notes": result}

        else:
            return {"error": f"Unknown tool: {name}"}

    except ValueError as e:
        return {"error": f"Invalid argument format: {str(e)}"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """Format tool execution result as a string for the LLM."""
    if "error" in result:
        return f"Tool {tool_name} failed: {result['error']}"

    if tool_name == "add_reminder":
        return f"Reminder created: {result.get('text', '')} (due: {result.get('due_at', '')}, id: {result.get('reminder_id', '')})"

    elif tool_name == "list_reminders":
        reminders = result.get("reminders", [])
        if not reminders:
            return "No pending reminders found."
        lines = ["Pending reminders:"]
        for r in reminders:
            lines.append(f"- {r['text']} (due: {r['due_at']}, id: {r['reminder_id']})")
        return "\n".join(lines)

    elif tool_name == "mark_reminder_done":
        return f"Reminder marked as done: {result.get('reminder_id', '')}"

    elif tool_name == "add_note":
        return f"Note saved: {result.get('content', '')} (id: {result.get('note_id', '')})"

    elif tool_name == "list_notes":
        notes = result.get("notes", [])
        if not notes:
            return "No notes found."
        lines = ["Recent notes:"]
        for n in notes:
            lines.append(f"- {n['content']} (created: {n['created_at']}, id: {n['note_id']})")
        return "\n".join(lines)

    return json.dumps(result)