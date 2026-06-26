"""
backend/scheduler/scheduler_setup.py
====================================
Core configuration and lifecycle initialization of APScheduler.
Provides job registry hooks.
"""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from backend.scheduler.utils import ensure_reports_directory, heartbeat_job
from backend.scheduler.jobs import execute_scheduled_report, parse_schedule_trigger

logger = logging.getLogger("scheduler.setup")

# Shared background scheduler instance
scheduler = None

def init_scheduler(app=None):
    """
    Initializes the BackgroundScheduler.
    Configures default verification jobs and ensures target directories exist.
    """
    global scheduler

    # 1. Initialize storage and folders
    ensure_reports_directory()

    # 2. Prevent double-start under Flask debugger's child process reloader
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true' and app and app.debug:
        logger.info("Scheduler initialization skipped in the primary reloader process.")
        return

    if scheduler is not None:
        logger.warning("Scheduler has already been initialized.")
        return

    logger.info("Initializing APScheduler BackgroundScheduler...")
    scheduler = BackgroundScheduler()

    # 3. Add default heartbeat check (runs every 30 seconds for local verification)
    scheduler.add_job(
        heartbeat_job,
        'interval',
        seconds=30,
        id='qa_heartbeat_job',
        replace_existing=True
    )
    logger.info("Registered local verification heartbeat job (30s interval).")

def start_scheduler():
    """Starts the background scheduler thread."""
    global scheduler
    if scheduler is None:
        logger.error("Cannot start: Scheduler has not been initialized yet.")
        return

    if not scheduler.running:
        logger.info("Starting background scheduler threads...")
        scheduler.start()
        logger.info("Background scheduler is now running.")
    else:
        logger.info("Background scheduler is already active.")

def shutdown_scheduler():
    """Gracefully shuts down the background scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        logger.info("Stopping background scheduler threads...")
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler has shut down.")
        scheduler = None

def register_scheduled_report(job_id: str, report_type: str, filters: dict | None,
                              export_format: str, interval: str, run_time: str):
    """
    Registry wrapper to register a scheduled report dynamically.
    Translates human readable interval/run_time parameters, builds the trigger, and schedules the job.
    """
    global scheduler
    if scheduler is None:
        logger.error("Scheduler not initialized. Cannot register job.")
        return False

    try:
        # Get cron arguments from parse_schedule_trigger
        trigger_args = parse_schedule_trigger(interval, run_time)
        
        # Add the job to scheduler
        scheduler.add_job(
            execute_scheduled_report,
            args=[report_type, filters, export_format, interval],
            id=job_id,
            replace_existing=True,
            **trigger_args
        )
        logger.info(f"Registered scheduled report job '{job_id}' successfully: Trigger={trigger_args}")
        return True
    except Exception as e:
        logger.error(f"Failed to register job '{job_id}': {e}", exc_info=True)
        return False
