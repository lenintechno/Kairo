#!/usr/bin/env python3
"""Direct agent test script for Step 6."""
import asyncio
from agent.assistant import run_assistant


async def test_agent():
    print("=" * 60)
    print("KAIRO AGENT DIRECT TEST")
    print("=" * 60)

    test_messages = [
        "Hello, how are you?",
        "Remind me to submit assignment tomorrow at 9am",
        "What are my reminders for today?",
        "Add a note: buy groceries after work",
        "List my notes",
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n--- Test {i}: '{msg}' ---")
        try:
            reply, tool_used = await run_assistant(msg)
            print(f"Tool used: {tool_used}")
            print(f"Reply: {reply}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent())