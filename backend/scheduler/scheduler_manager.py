"""
backend/scheduler/scheduler_manager.py
======================================
Manages the lifecycle of the APScheduler background scheduler.
Initializes, starts, and stops scheduled tasks.
"""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

# Global scheduler instance
scheduler = None

# Directory where generated reports will be saved
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scheduler",
    "output"
)

def heartbeat_job():
    """A simple dummy job to verify the scheduler is running successfully."""
    logger.info("Scheduler heartbeat: The background scheduler is active and running successfully.")

def init_scheduler(app=None):
    """
    Initializes the BackgroundScheduler.
    Creates output directories and configures default jobs.
    """
    global scheduler

    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        logger.info(f"Created report output directory at: {OUTPUT_DIR}")

    # Prevent double-initialization in Flask's debug mode (reloader process)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' and app and app.debug:
        logger.info("Skipping scheduler initialization in the parent reloader process.")
        return

    if scheduler is not None:
        logger.warning("Scheduler is already initialized.")
        return

    logger.info("Initializing BackgroundScheduler...")
    scheduler = BackgroundScheduler()

    # Add dummy job to fire every 1 minute for verification
    scheduler.add_job(
        heartbeat_job,
        'interval',
        minutes=1,
        id='heartbeat_job',
        replace_existing=True
    )
    logger.info("Registered heartbeat dummy job (runs every 1 minute).")

def start_scheduler():
    """Starts the scheduler if it has been initialized and is not already running."""
    global scheduler
    if scheduler is None:
        logger.error("Cannot start scheduler: Scheduler has not been initialized. Call init_scheduler() first.")
        return

    if not scheduler.running:
        logger.info("Starting background scheduler...")
        scheduler.start()
        logger.info("Background scheduler started successfully.")
    else:
        logger.info("Background scheduler is already running.")

def shutdown_scheduler():
    """Stops the scheduler gracefully."""
    global scheduler
    if scheduler and scheduler.running:
        logger.info("Shutting down background scheduler...")
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler shut down successfully.")
        scheduler = None
