## Scheduler & Automation Module - Group 4

- The scheduling and automation feature is handled inside `backend/scheduler/`. 
- It uses APScheduler to run background jobs while the Flask app is running.
- This module supports recurring report generation such as daily, weekly, and monthly reports.

### Scheduler Files:
```
backend/scheduler/
├── scheduler_manager.py # Scheduler lifecycle management
├── scheduler_setup.py   # Scheduler initialization and job registration
├── utils.py             # Folder creation, filenames, heartbeat test job
├── jobs.py              # Scheduled report execution logic
└── test_jobs.py         # Scheduler tests 
```

 ### Main Functions
 The scheduler module includes:
  - `ensure_reports_directory()` - creates `backend/generated_reports/` if it does not exist.
  - `generate_report_filename(report_type, export_format)` - creates clean timestamped filenames.
  - `heartbeat_job()` - runs a lightweight test job every 30 seconds to verify scheduler activity.
  - `execute_scheduled_report()` - runs the real scheduled report generation logic.
  - `parse_schedule_trigger()` - converts schedule settings into APScheduler trigger settings.
  - `register_scheduled_report()` - registers a recurring report job with the scheduler.

### Local Scheduler Test
Run this command from the project root:
```bash
python backend/scheduler/utils.py
```
Expected terminal output:
```
[SCHEDULER HEARTBEAT] Job fired successfully at ...
[SCHEDULER HEARTBEAT] Test file created: backend/generated_reports/...
```

A heartbeat .txt file should be created inside:
`backend/generated_reports/`

This confirms that the scheduler utility can create the output folder, generate timestamped filenames, create a test file, and print logs correctly in the terminal.

### Adding a New Schedule
New recurring jobs can be added using APScheduler's add_job() method.

Example weekly schedule:
```text
scheduler.add_job(
    execute_scheduled_report,
    trigger='cron',
    day_of_week='mon',
    hour=8,
    minute=0,
    id='weekly_sales_report',
    replace_existing=True
)
```

### Scheduled Report Flow
```
Scheduler starts
        ↓
Scheduled job fires
        ↓
execute_scheduled_report() runs
        ↓
Report generation function is called
        ↓
Output folder is checked or created
        ↓
Clean timestamped filename is generated
        ↓
PDF or Excel report is saved into backend/generated_reports/
```

### Generated Reports
Generated report files are saved in:
`backend/generated_reports/`

This folder should be ignored in Git using:
```gitignore
backend/generated_reports/
```