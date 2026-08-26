from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import REMINDER_CHECK_INTERVAL_SECONDS
from db.supabase_client import get_due_pending_reminders, mark_reminder_notified
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def check_due_reminders():
    """Check for due reminders and mark them as notified."""
    try:
        due_reminders = get_due_pending_reminders()
        if due_reminders:
            logger.info(f"Found {len(due_reminders)} due reminder(s)")
            for reminder in due_reminders:
                reminder_id = reminder["reminder_id"]
                mark_reminder_notified(reminder_id)
                logger.info(f"Marked reminder {reminder_id} as notified: {reminder['text']}")
        else:
            logger.debug("No due reminders found")
    except Exception as e:
        logger.error(f"Error checking due reminders: {e}")


def start_scheduler():
    """Start the APScheduler background job."""
    scheduler.add_job(
        check_due_reminders,
        trigger=IntervalTrigger(seconds=REMINDER_CHECK_INTERVAL_SECONDS),
        id="reminder_checker",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started: checking reminders every {REMINDER_CHECK_INTERVAL_SECONDS}s")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")