"""
backend/scheduler/utils.py
==========================

Utility functions for Group 4 - Scheduling & Automation.

This file provides:
1. A helper function to create the generated reports folder automatically.
2. A helper function to generate clean timestamped filenames.
3. A lightweight heartbeat job for local scheduler testing.
"""

from datetime import datetime
from pathlib import Path


REPORTS_DIRECTORY = Path("backend/generated_reports")


def ensure_reports_directory(directory_path=REPORTS_DIRECTORY):
    """
    Create the generated reports folder if it does not already exist.

    Args:
        directory_path (Path or str): Folder path where generated reports are saved.

    Returns:
        Path: Existing or newly created reports folder path.
    """
    reports_directory = Path(directory_path)
    reports_directory.mkdir(parents=True, exist_ok=True)
    return reports_directory


def generate_report_filename(report_type, export_format):
    """
    Generate a clean timestamped filename for a report.

    Args:
        report_type (str): Report type such as sales, user_activity, inventory.
        export_format (str): Output format such as pdf, xlsx, or txt.

    Returns:
        str: Clean timestamped filename.
    """
    clean_report_type = report_type.strip().lower().replace(" ", "_")
    clean_export_format = export_format.strip().lower().replace(".", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{clean_report_type}_report_{timestamp}.{clean_export_format}"


def heartbeat_job():
    """
    Lightweight local test job to verify that APScheduler fires correctly.

    This job creates a small text file inside backend/generated_reports/
    and prints a log message in the terminal.
    """
    reports_directory = ensure_reports_directory()
    filename = generate_report_filename("scheduler_heartbeat", "txt")
    file_path = reports_directory / filename

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Scheduler heartbeat job executed successfully.\n")
        file.write(f"Execution time: {current_time}\n")

    print(f"[SCHEDULER HEARTBEAT] Job fired successfully at {current_time}")
    print(f"[SCHEDULER HEARTBEAT] Test file created: {file_path}")


if __name__ == "__main__":
    heartbeat_job()