
"""
backend/scheduler/test_jobs.py
==============================
Member 2 — Group 4 (Scheduling & Automation)

Tests for execute_scheduled_report() and parse_schedule_trigger().

Run from the project root:
    pytest backend/scheduler/test_jobs.py -v

These tests use unittest.mock to patch Group 2's generate_report()
so they run WITHOUT a database connection.
"""

import io
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# ── Ensure project root is on sys.path ───────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.scheduler.jobs import (
    execute_scheduled_report,
    parse_schedule_trigger,
    run_sales_excel,
    run_sales_pdf,
    run_user_activity_excel,
    run_user_activity_pdf,
    run_inventory_excel,
    run_inventory_pdf,
    VALID_REPORT_TYPES,
    VALID_FORMATS,
    REPORTS_DIR,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures & helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fake_stream(content: bytes = b"FAKE REPORT CONTENT") -> io.BytesIO:
    """Return a BytesIO that mimics what generate_report() returns."""
    buf = io.BytesIO(content)
    buf.seek(0)
    return buf


def _cleanup(path: str | None):
    """Remove a generated file after a test if it exists."""
    if path and Path(path).is_file():
        Path(path).unlink()


MOCK_TARGET = "backend.scheduler.jobs._call_group2_generator"


# ─────────────────────────────────────────────────────────────────────────────
# execute_scheduled_report — all 6 type × format combinations
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("report_type", sorted(VALID_REPORT_TYPES))
@pytest.mark.parametrize("export_format", sorted(VALID_FORMATS))
def test_all_combinations_create_file(report_type, export_format):
    """Every report_type × export_format combination must produce a real file."""
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        path = execute_scheduled_report(report_type, export_format=export_format)

    assert path is not None, f"Expected a file path for {report_type}/{export_format}"
    assert Path(path).is_file(), f"File does not exist on disk: {path}"
    assert Path(path).stat().st_size > 0, f"File is empty: {path}"
    _cleanup(path)


# ─────────────────────────────────────────────────────────────────────────────
# File naming checks
# ─────────────────────────────────────────────────────────────────────────────

def test_filename_contains_report_type():
    """Saved filename must embed the report type."""
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        path = execute_scheduled_report("inventory", export_format="pdf")
    assert "inventory" in Path(path).name
    _cleanup(path)


def test_excel_filename_has_xlsx_extension():
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        path = execute_scheduled_report("sales", export_format="excel")
    assert path.endswith(".xlsx"), f"Expected .xlsx, got: {path}"
    _cleanup(path)


def test_pdf_filename_has_pdf_extension():
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        path = execute_scheduled_report("sales", export_format="pdf")
    assert path.endswith(".pdf"), f"Expected .pdf, got: {path}"
    _cleanup(path)


def test_filenames_are_unique_across_calls():
    """Two consecutive calls must produce different filenames (timestamp-based)."""
    import time
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        p1 = execute_scheduled_report("inventory", export_format="excel")
    time.sleep(1)
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        p2 = execute_scheduled_report("inventory", export_format="excel")
    assert p1 != p2, "Filenames must be unique across calls"
    _cleanup(p1)
    _cleanup(p2)


# ─────────────────────────────────────────────────────────────────────────────
# Output directory is created
# ─────────────────────────────────────────────────────────────────────────────

def test_output_directory_is_created():
    """The reports directory must exist after a successful job."""
    with patch(MOCK_TARGET, return_value=_fake_stream()):
        path = execute_scheduled_report("sales", export_format="excel")
    assert REPORTS_DIR.is_dir(), "Reports directory was not created"
    _cleanup(path)


# ─────────────────────────────────────────────────────────────────────────────
# Filters are forwarded to Group 2
# ─────────────────────────────────────────────────────────────────────────────

def test_filters_are_forwarded_to_generator():
    """execute_scheduled_report must pass filters through to _call_group2_generator."""
    filters = {"start_date": "2026-01-01", "end_date": "2026-06-30", "region": "Western Province"}
    with patch(MOCK_TARGET, return_value=_fake_stream()) as mock_gen:
        path = execute_scheduled_report("sales", filters=filters, export_format="excel")
    mock_gen.assert_called_once_with("sales", filters, "excel")
    _cleanup(path)


def test_none_filters_defaults_to_empty_dict():
    """None filters must be normalised to {} before being passed to the generator."""
    with patch(MOCK_TARGET, return_value=_fake_stream()) as mock_gen:
        path = execute_scheduled_report("sales", filters=None, export_format="excel")
    _, call_filters, _ = mock_gen.call_args[0]
    assert call_filters == {}, "Filters should default to empty dict, not None"
    _cleanup(path)


# ─────────────────────────────────────────────────────────────────────────────
# Error handling — invalid inputs
# ─────────────────────────────────────────────────────────────────────────────

def test_invalid_report_type_returns_none():
    result = execute_scheduled_report("unknown_type", export_format="excel")
    assert result is None, "Should return None for unknown report_type"


def test_invalid_export_format_returns_none():
    result = execute_scheduled_report("sales", export_format="docx")
    assert result is None, "Should return None for unsupported format"


def test_generator_exception_returns_none():
    """If Group 2's generator raises, the job must return None (not crash)."""
    with patch(MOCK_TARGET, side_effect=RuntimeError("DB connection failed")):
        result = execute_scheduled_report("sales", export_format="excel")
    assert result is None, "Should return None when generator raises"


# ─────────────────────────────────────────────────────────────────────────────
# Convenience wrapper tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("wrapper,expected_type,expected_format", [
    (run_sales_excel,          "sales",         "excel"),
    (run_sales_pdf,            "sales",         "pdf"),
    (run_user_activity_excel,  "user_activity", "excel"),
    (run_user_activity_pdf,    "user_activity", "pdf"),
    (run_inventory_excel,      "inventory",     "excel"),
    (run_inventory_pdf,        "inventory",     "pdf"),
])
def test_convenience_wrappers(wrapper, expected_type, expected_format):
    """Each convenience wrapper must call the generator with correct args."""
    with patch(MOCK_TARGET, return_value=_fake_stream()) as mock_gen:
        path = wrapper()
    called_type, _, called_format = mock_gen.call_args[0]
    assert called_type   == expected_type,   f"Expected type={expected_type}, got {called_type}"
    assert called_format == expected_format, f"Expected format={expected_format}, got {called_format}"
    _cleanup(path)


# ─────────────────────────────────────────────────────────────────────────────
# parse_schedule_trigger tests
# ─────────────────────────────────────────────────────────────────────────────

def test_daily_trigger():
    result = parse_schedule_trigger("daily", "09:00")
    assert result == {"trigger": "cron", "hour": 9, "minute": 0}


def test_weekly_trigger():
    result = parse_schedule_trigger("weekly", "09:00")
    assert result["trigger"]     == "cron"
    assert result["day_of_week"] == "mon"
    assert result["hour"]        == 9
    assert result["minute"]      == 0


def test_monthly_trigger():
    result = parse_schedule_trigger("monthly", "09:00")
    assert result["trigger"] == "cron"
    assert result["day"]     == 1
    assert result["hour"]    == 9
    assert result["minute"]  == 0


def test_trigger_parses_minutes_correctly():
    result = parse_schedule_trigger("daily", "14:30")
    assert result["hour"]   == 14
    assert result["minute"] == 30


def test_invalid_interval_raises():
    with pytest.raises(ValueError, match="Unknown interval"):
        parse_schedule_trigger("hourly", "09:00")


def test_invalid_run_time_raises():
    with pytest.raises(ValueError, match="Invalid run_time"):
        parse_schedule_trigger("daily", "not-a-time")


def test_case_insensitive_interval():
    result = parse_schedule_trigger("DAILY", "08:00")
    assert result["trigger"] == "cron"
