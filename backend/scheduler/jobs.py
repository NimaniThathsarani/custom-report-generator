"""
backend/scheduler/jobs.py
=========================
Member 2 — Group 4 (Scheduling & Automation)

This module contains the logic that runs when a scheduled job fires.
It calls Group 2's report-generation function (backend.app.generate_report),
saves the output file to backend/generated_reports/, and logs the result.

Supports:
  - All 3 report types : sales | user_activity | inventory
  - Both export formats : excel | pdf
  - Flexible schedule intervals via parse_schedule_trigger()
"""

import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("scheduler.jobs")

# ── Output directory (must match utils.py → REPORTS_DIRECTORY) ───────────────
REPORTS_DIR = Path("backend/generated_reports")

# ── Valid values (used for input validation) ──────────────────────────────────
VALID_REPORT_TYPES = {"sales", "user_activity", "inventory"}
VALID_FORMATS      = {"excel", "pdf"}
FORMAT_EXTENSION   = {"excel": "xlsx", "pdf": "pdf"}


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_dir(directory: Path) -> Path:
    """Create the reports directory if it does not already exist."""
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _make_filename(report_type: str, export_format: str) -> str:
    """
    Build a clean, timestamped filename.

    Example:
        sales_report_20260626_143022.xlsx
        user_activity_report_20260626_143022.pdf
    """
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = FORMAT_EXTENSION[export_format]
    return f"{report_type}_report_{ts}.{ext}"


def _call_group2_generator(report_type: str,
                            filters: dict | None,
                            export_format: str):
    """
    Import and call Group 2's generate_report() from backend.app.

    Returns an io.BytesIO stream (seek position 0) on success,
    or raises an exception on failure.
    """
    # Lazy import so the scheduler still starts if DB is not yet ready
    from backend.app import generate_report          # Group 2's public API
    filters = filters or {}
    stream = generate_report(report_type, filters, export_format)
    return stream


def _save_stream_to_file(stream, output_path: Path) -> bool:
    """
    Write an io.BytesIO stream to disk.

    Returns True if the file was written and is non-empty, False otherwise.
    """
    try:
        with open(output_path, "wb") as f:
            f.write(stream.read())
        return output_path.is_file() and output_path.stat().st_size > 0
    except OSError as exc:
        logger.error("Failed to write report file '%s': %s", output_path, exc)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point — called by APScheduler
# ─────────────────────────────────────────────────────────────────────────────

def execute_scheduled_report(report_type: str,
                              filters: dict | None = None,
                              export_format: str = "excel",
                              interval: str = "daily") -> str | None:
    """
    Main job function executed by APScheduler when a scheduled trigger fires.

    Parameters
    ----------
    report_type   : "sales" | "user_activity" | "inventory"
    filters       : optional dict of filter keys/values passed to the data layer
                    Sales      → start_date, end_date, category, region
                    Activity   → start_date, end_date, username, activity_type
                    Inventory  → category, warehouse_location
    export_format : "excel" | "pdf"
    interval      : human-readable label for logging only ("daily", "weekly", …)

    Returns
    -------
    str   — absolute path to the saved file on success
    None  — on any validation or generation failure
    """
    # ── 1. Validate inputs ────────────────────────────────────────────────────
    report_type   = report_type.strip().lower()
    export_format = export_format.strip().lower()

    if report_type not in VALID_REPORT_TYPES:
        logger.error(
            "Invalid report_type '%s'. Must be one of: %s",
            report_type, sorted(VALID_REPORT_TYPES)
        )
        return None

    if export_format not in VALID_FORMATS:
        logger.error(
            "Invalid export_format '%s'. Must be one of: %s",
            export_format, sorted(VALID_FORMATS)
        )
        return None

    # ── 2. Prepare output path ────────────────────────────────────────────────
    _ensure_dir(REPORTS_DIR)
    filename    = _make_filename(report_type, export_format)
    output_path = REPORTS_DIR / filename

    logger.info(
        "⏰  Scheduled job fired | type=%-15s  format=%-5s  interval=%s",
        report_type, export_format, interval
    )

    # ── 3. Call Group 2's report generator ────────────────────────────────────
    try:
        stream = _call_group2_generator(report_type, filters, export_format)
    except Exception as exc:
        logger.exception(
            "❌  Report generation failed for %s/%s: %s",
            report_type, export_format, exc
        )
        return None

    # ── 4. Save the file ──────────────────────────────────────────────────────
    saved = _save_stream_to_file(stream, output_path)

    if saved:
        size_kb = output_path.stat().st_size / 1024
        logger.info(
            "✅  Report saved: %s  (%.1f KB)",
            output_path.resolve(), size_kb
        )
        return str(output_path.resolve())
    else:
        logger.error(
            "❌  Generator completed but file is missing or empty: %s",
            output_path
        )
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Schedule trigger parser — used by scheduler_setup.register_scheduled_report()
# ─────────────────────────────────────────────────────────────────────────────

def parse_schedule_trigger(interval: str, run_time: str) -> dict:
    """
    Convert human-readable schedule parameters into APScheduler cron kwargs.

    Parameters
    ----------
    interval : "daily" | "weekly" | "monthly"
    run_time : "HH:MM"  (24-hour format, e.g. "09:00")

    Returns
    -------
    dict of kwargs to unpack into scheduler.add_job(..., trigger='cron', **kwargs)

    Examples
    --------
    >>> parse_schedule_trigger("daily", "09:00")
    {'trigger': 'cron', 'hour': 9, 'minute': 0}

    >>> parse_schedule_trigger("weekly", "09:00")
    {'trigger': 'cron', 'day_of_week': 'mon', 'hour': 9, 'minute': 0}

    >>> parse_schedule_trigger("monthly", "09:00")
    {'trigger': 'cron', 'day': 1, 'hour': 9, 'minute': 0}
    """
    # Parse run_time → hour, minute
    try:
        time_parts = run_time.strip().split(":")
        hour   = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    except (ValueError, IndexError):
        raise ValueError(
            f"Invalid run_time '{run_time}'. Expected HH:MM format, e.g. '09:00'."
        )

    interval = interval.strip().lower()

    if interval == "daily":
        return {"trigger": "cron", "hour": hour, "minute": minute}

    elif interval == "weekly":
        # Default to every Monday — a common business cadence
        return {"trigger": "cron", "day_of_week": "mon", "hour": hour, "minute": minute}

    elif interval == "monthly":
        # First day of every month
        return {"trigger": "cron", "day": 1, "hour": hour, "minute": minute}

    else:
        raise ValueError(
            f"Unknown interval '{interval}'. Supported: 'daily', 'weekly', 'monthly'."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Convenience wrappers — APScheduler job IDs can point to these directly
# ─────────────────────────────────────────────────────────────────────────────

def run_sales_excel():
    """Convenience wrapper: generate a Sales Excel report."""
    return execute_scheduled_report("sales", export_format="excel")

def run_sales_pdf():
    """Convenience wrapper: generate a Sales PDF report."""
    return execute_scheduled_report("sales", export_format="pdf")

def run_user_activity_excel():
    """Convenience wrapper: generate a User Activity Excel report."""
    return execute_scheduled_report("user_activity", export_format="excel")

def run_user_activity_pdf():
    """Convenience wrapper: generate a User Activity PDF report."""
    return execute_scheduled_report("user_activity", export_format="pdf")

def run_inventory_excel():
    """Convenience wrapper: generate an Inventory Excel report."""
    return execute_scheduled_report("inventory", export_format="excel")

def run_inventory_pdf():
    """Convenience wrapper: generate an Inventory PDF report."""
    return execute_scheduled_report("inventory", export_format="pdf")
