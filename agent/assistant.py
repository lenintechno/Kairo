import google.generativeai as genai
from config import GEMINI_API_KEY, LLM_MODEL
from agent.tools import TOOLS
from agent.tool_executor import execute_tool, format_tool_result
from db.supabase_client import log_message, get_conversation_history
from datetime import datetime
from typing import Optional


# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# System prompt with current datetime for resolution
def get_system_prompt() -> str:
    now = datetime.now().isoformat()
    return f"""You are Kairo, a personal AI automation assistant. You help users by taking real actions — setting reminders, saving notes, listing them — not just chatting.

Current server time: {now}

When the user asks to set a reminder, resolve relative times (e.g., "tomorrow at 5pm", "in 30 minutes") to an absolute ISO 8601 datetime using the current server time above. Then call add_reminder with the resolved datetime.

When listing reminders, default to filter "today" unless the user specifies otherwise.

Available tools:
- add_reminder: Create a reminder (requires text and due_at as ISO datetime)
- list_reminders: Get pending reminders (filter: today, week, all)
- mark_reminder_done: Mark a reminder complete (requires reminder_id)
- add_note: Save a note (requires content)
- list_notes: Get recent notes (optional limit, default 10)

Always use tools when the user's request matches an available action. Only respond conversationally when no tool applies."""


async def run_assistant(user_message: str) -> tuple[str, Optional[str]]:
    """
    Run the tool-calling loop.
    Returns (reply_text, tool_used_name_or_none).
    """
    # Log user message
    log_message("user", user_message)

    # Initialize model with tools
    model = genai.GenerativeModel(
        model_name=LLM_MODEL,
        tools=TOOLS,
        system_instruction=get_system_prompt(),
    )

    # Get recent conversation history for context
    history = get_conversation_history(limit=10)
    chat_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        chat_history.append({"role": role, "parts": [msg["content"]]})

    # Start chat with history
    chat = model.start_chat(history=chat_history)

    # Send user message
    response = await chat.send_message_async(user_message)

    tool_used = None

    # Tool-calling loop: keep going while model returns function calls
    while response.candidates and response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]

        if hasattr(part, "function_call") and part.function_call:
            # Execute the tool
            fc = part.function_call
            tool_name = fc.name
            tool_used = tool_name
            args = dict(fc.args) if fc.args else {}

            result = await execute_tool(tool_name, args)
            formatted = format_tool_result(tool_name, result)

            # Send tool result back to model
            response = await chat.send_message_async(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": formatted},
                    )
                )
            )
        else:
            # Plain text response - we're done
            reply = response.text if response.text else ""
            break

    # Log assistant reply
    if reply:
        log_message("assistant", reply)

    return reply, tool_used