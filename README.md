# Kairo

> **Kairo** — from *kairos*, "the right, opportune moment."  
> A voice-driven personal automation agent that listens to spoken requests, decides which action to take — set a reminder, save a note, or just respond — and speaks back, using LLM tool-calling instead of scripted commands.

## Live Demo

**Deployed URL:** `https://kairo.onrender.com` (or your Render URL after deployment)

> **Note:** Free-tier Render Web Services may take ~30–60 seconds to wake on first load. Please wait for the cold start.

## Architecture Summary

Kairo is a single-page voice interface served by a FastAPI backend. The browser handles speech recognition (STT) and speech synthesis (TTS) via the Web Speech API. Each user utterance is sent to `/chat`, where a Gemini 2.5 Flash model (via native function calling) decides which tool to invoke:

| Tool | Purpose |
|------|---------|
| `add_reminder` | Create a reminder with text and ISO datetime |
| `list_reminders` | Get pending reminders (filter: today / week / all) |
| `mark_reminder_done` | Mark a reminder complete |
| `add_note` | Save a quick note |
| `list_notes` | Retrieve recent notes (default 10) |

Tools execute against Supabase (Postgres). A background APScheduler job polls for due reminders every 60s, marks them `notified`, and the frontend polls `/reminders/due` every 10s to speak proactive notifications via TTS.

**Stack:** Python 3.11+, FastAPI, Gemini API (`gemini-2.5-flash`), Supabase, APScheduler, Web Speech API. Deployed as a single Render Web Service serving both API and static frontend.

## Setup (Local)

```bash
# 1. Clone
git clone <your-repo-url>
cd kairo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your keys:
#   GEMINI_API_KEY=...
#   SUPABASE_URL=...
#   SUPABASE_KEY=...

# 4. Create Supabase tables (run in Supabase Dashboard SQL Editor)
# See db/schema.sql or the spec for exact DDL

# 5. Run locally
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 6. Open http://localhost:8000 in Chrome or Edge
# Click the orb or press SPACE to speak
```

## Project Structure

```
kairo/
├── .env                        # gitignored — your keys
├── .env.example                # template
├── .gitignore
├── requirements.txt
├── config.py                   # loads env with defaults
├── db/
│   └── supabase_client.py      # all CRUD for reminders, notes, conversation_log
├── agent/
│   ├── tools.py                # 5 tool schemas for Gemini function calling
│   ├── tool_executor.py        # maps tool name -> DB function
│   └── assistant.py            # tool-calling loop + system prompt with current datetime
├── scheduler/
│   └── reminder_checker.py     # APScheduler: marks due reminders as "notified"
├── api/
│   ├── schemas.py              # Pydantic models for /chat, /reminders/due, /health
│   └── main.py                 # FastAPI app + lifespan + static file mount
├── web/
│   └── index.html              # single-page UI (orb, transcript, reminders ticker)
└── README.md
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase **service role** key (sb_secret_...) — backend only |
| `LLM_MODEL` | No | Default: `gemini-2.5-flash` |
| `REMINDER_CHECK_INTERVAL_SECONDS` | No | Default: `60` |
| `PORT` | No | Default: `8000` (Render injects `$PORT`) |

## Deployment (Render)

1. Push to a **public** GitHub repo. Confirm `.env` is in `.gitignore` and not committed.
2. Render → **New → Web Service** → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. In Render's **Environment** tab, add:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
6. Deploy. Render will serve both API and frontend from the same URL.
7. Test the live URL end-to-end (mic → reminder created → spoken confirmation) before submitting.

## Acceptance Criteria (Section 15)

- [ ] Speaking "remind me to submit assignment tomorrow at 9am" creates a correctly-dated reminder with spoken confirmation.
- [ ] Speaking "what are my reminders for today" lists them back, spoken aloud.
- [ ] An unrelated message gets a normal conversational reply, no forced tool call.
- [ ] A due reminder triggers a spoken notification proactively.
- [ ] The live Render URL demonstrates all of the above on first load (accounting for free-tier wake time).

## License

MIT — built independently for the AI automation agent challenge.