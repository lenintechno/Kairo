TOOLS = [
    {
        "name": "add_reminder",
        "description": "Create a new reminder for the user. Use this when the user asks to be reminded of something at a specific time.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text": {
                    "type": "STRING",
                    "description": "The reminder text, e.g., 'submit assignment' or 'call mom'."
                },
                "due_at": {
                    "type": "STRING",
                    "description": "ISO 8601 datetime when the reminder is due, e.g., '2026-08-27T09:00:00'."
                }
            },
            "required": ["text", "due_at"]
        }
    },
    {
        "name": "list_reminders",
        "description": "Get the user's pending reminders. Can filter by time range.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filter": {
                    "type": "STRING",
                    "enum": ["today", "week", "all"],
                    "description": "Time range filter: 'today' for reminders due today, 'week' for this week, 'all' for all pending reminders."
                }
            },
            "required": ["filter"]
        }
    },
    {
        "name": "mark_reminder_done",
        "description": "Mark a reminder as completed/done.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reminder_id": {
                    "type": "STRING",
                    "description": "The UUID of the reminder to mark as done."
                }
            },
            "required": ["reminder_id"]
        }
    },
    {
        "name": "add_note",
        "description": "Save a quick note for the user.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "content": {
                    "type": "STRING",
                    "description": "The note content to save."
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "list_notes",
        "description": "Retrieve the user's recent notes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "limit": {
                    "type": "INTEGER",
                    "description": "Maximum number of notes to return (default 10)."
                }
            },
            "required": []
        }
    }
]