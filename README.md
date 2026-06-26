# Custom Report Generator

**Enable stakeholders to generate reports on demand.**

Instead of manually pulling data and building a report every time someone asks for one, stakeholders can log in, pick a report type, set filters (like a date range), click **Generate**, and get their report instantly — or have it delivered automatically on a recurring schedule.

---

## Tech Stack

| Layer                          | Technology              |
| ------------------------------ | ----------------------- |
| Frontend                       | HTML / CSS / JavaScript |
| Backend                        | Flask (Python)          |
| Database                       | MySQL                   |
| Data Processing                | Pandas                  |
| Excel Report Output            | OpenPyXL                |
| PDF Report Output              | ReportLab               |
| Scheduling (Recurring Reports) | APScheduler             |
| Version Control                | GitHub                  |

---

## Features

- Multiple report types with adjustable filters/parameters (date range, category, region, etc.)
- Simple, non-technical interface for selecting a report and generating it
- Reports exportable as Excel and PDF
- Recurring/scheduled report generation
- Full user and technical documentation

---

## Folder Structure

```
custom-report-generator/
├── README.md
├── .gitignore
├── requirements.txt
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── models/                 # Database models / schema mapping
│   ├── routes/                 # API endpoints
│   ├── templates_engine/       # OpenPyXL + ReportLab report builders
│   └── scheduler/              # APScheduler scheduling and automation
│       ├── scheduler_manager.py 
│       ├── scheduler_setup.py   
│       ├── utils.py             
│       ├── jobs.py              
│       └── test_jobs.py                  
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── database/
│   ├── schema.sql              # Table definitions
│   └── seed_data.sql           # mock/sample data seeder
├── docs/
│   ├── requirements.md         # Report types, fields, filters
│   ├── report_specifications.md  # Technical: what each report pulls
│   └── user_guide.md           # End-user instructions
└── tests/
```

---

## Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/<org>/custom-report-generator.git
   cd custom-report-generator
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up MySQL:
   - Add mysql bin/ into system variables from XAMPP or MySQL Server
   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p report_generator < database/seed_data.sql
   ```
4. Add a `.env` file (not committed) with your DB credentials:
   ```bash
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=yourpassword
   DB_NAME=report_generator
   ```
5. Run the Flask app:
   ```bash
   python backend/app.py
   ```
6. Open `frontend/index.html` in your browser (or serve it via Flask's static folder).

---

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

---

## Team & Group Ownership

| Group   | Focus Area                    | Folder(s) Owned                                                              |
| ------- | ----------------------------- | ---------------------------------------------------------------------------- |
| Group 1 | Requirements & Report Design  | `docs/requirements.md`                                                       |
| Group 2 | Report Templates & Data Layer | `database/`, `backend/models/`, `backend/templates_engine/`,`backend/app.py` |
| Group 3 | User Interface                | `frontend/`                                                                  |
| Group 4 | Scheduling & Automation       | `backend/scheduler/`                                                         |
| Group 5 | Documentation & Testing       | `docs/user_guide.md`, `docs/report_specifications.md`, `tests/`              |

---

## Branch & PR Workflow

- `main` always stays stable and working — never commit directly to it.
- Each group works on its own branch:
  - `group1-requirements`
  - `group2-backend`, `group2-templates`
  - `group3-ui`
  - `group4-scheduler`
  - `group5-docs`
- Open a Pull Request into `main` when a piece of work is ready.
- Commit early and often — small commits are easier to review and merge than one giant commit at the end.
