# Custom Report Generator

A web-based application that enables stakeholders to generate customized business reports on demand, apply filters, download PDF or Excel files, and schedule recurring reports for automatic email delivery.

# Project Overview

The Custom Report Generator is built as part of an academic group project. It allows non-technical stakeholders to generate business reports without requiring developer assistance. Users can select a report type, apply relevant filters, download the result in PDF or Excel format, and set up recurring schedules to receive reports automatically by email.


# Features

- Generate reports on demand
- Apply dynamic filters by report type
- Download reports as PDF or Excel
- Schedule recurring reports (Daily / Weekly / Monthly)
- Automatic email delivery of scheduled reports

##  Report Types

| Report | Filters Available |
|---|---|
| Sales Report | Date Range, Product Category, Region |
| User Activity Report | Date Range, User Name, Activity Type |
| Inventory Report | Product Category, Warehouse Location |

---
## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python (Flask) |
| Database | MySQL |
| PDF Reports | ReportLab |
| Excel Reports | OpenPyXL |
| Data Processing | Pandas |
| Scheduling | APScheduler |
| Design | Figma |
| Documentation | Google Docs |
| Version Control | GitHub |

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
   git clone https://github.com/NimaniThathsarani/custom-report-generator.git
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

## Team & Group Ownership

| Group   | Focus Area                    | Folder(s) Owned                                                              |
| ------- | ----------------------------- | ---------------------------------------------------------------------------- |
| Group 1 | Requirements & Report Design  | `docs/requirements.md`                                                       |
| Group 2 | Report Templates & Data Layer | `database/`, `backend/models/`, `backend/templates_engine/`,`backend/app.py` |
| Group 3 | User Interface                | `frontend/`                                                                  |
| Group 4 | Scheduling & Automation       | `backend/scheduler/`                                                         |
| Group 5 | Documentation & Testing       | `docs/user_guide.md`, `docs/report_specifications.md`, `tests/`              |

---


