# Custom Report Generator

**Enable stakeholders to generate reports on demand.**

Instead of manually pulling data and building a report every time someone asks for one, stakeholders can log in, pick a report type, set filters (like a date range), click **Generate**, and get their report instantly — or have it delivered automatically on a recurring schedule.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML / CSS / JavaScript |
| Backend | Flask (Python) |
| Database | MySQL |
| Data Processing | Pandas |
| Excel Report Output | OpenPyXL |
| PDF Report Output | ReportLab |
| Scheduling (Recurring Reports) | APScheduler |
| Version Control | GitHub |

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
│   └── scheduler/              # APScheduler jobs
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── database/
│   └── schema.sql              # Table definitions + mock/sample data
├── docs/
│   ├── requirements.md         # Report types, fields, filters
│   ├── report_specifications.md  # Technical: what each report pulls
│   └── user_guide.md           # End-user instructions
└── tests/
```

---

## Setup Instructions

1. Clone the repo:
   ```
   git clone https://github.com/<org>/custom-report-generator.git
   cd custom-report-generator
   ```
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up MySQL:
   - Create a database named `report_generator`
   - Run `database/schema.sql` to create tables and load mock data
4. Add a `.env` file (not committed) with your DB credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=yourpassword
   DB_NAME=report_generator
   ```
5. Run the Flask app:
   ```
   python backend/app.py
   ```
6. Open `frontend/index.html` in your browser (or serve it via Flask's static folder).

---

## Team & Group Ownership

| Group | Focus Area | Folder(s) Owned |
|---|---|---|
| Group 1 | Requirements & Report Design | `docs/requirements.md` |
| Group 2 | Report Templates & Data Layer | `database/`, `backend/models/`, `backend/templates_engine/`,`backend/app.py` |
| Group 3 | User Interface | `frontend/` |
| Group 4 | Scheduling & Automation | `backend/scheduler/` |
| Group 5 | Documentation & Testing | `docs/user_guide.md`, `docs/report_specifications.md`, `tests/` |

See [Detailed Group Breakdown](#detailed-group-breakdown) below for exactly what each group should build.

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
