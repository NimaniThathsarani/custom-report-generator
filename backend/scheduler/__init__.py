# backend/scheduler/__init__.py
# Exposes scheduler lifecycle functions for easy import by other modules.
from backend.scheduler.scheduler_setup import (
    init_scheduler,
    start_scheduler,
    shutdown_scheduler,
    register_scheduled_report
)
