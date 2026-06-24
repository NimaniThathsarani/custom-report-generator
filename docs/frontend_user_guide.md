# User Guide — Custom Report Generator

> **For non-technical stakeholders, managers, and end users.**
> This guide explains how to use the Custom Report Generator to create, download, and schedule reports — no technical knowledge required.

---

## What Is This Tool?

The Custom Report Generator lets you instantly create business reports without needing to ask the IT team. You can:

- Generate a **Sales Report** to see revenue, orders, and regional performance
- Generate a **User Activity Report** to see how the system is being used
- Generate an **Inventory Report** to check stock levels across warehouses
- Download your report as a **PDF** (for printing and presentations) or **Excel** (for analysis)
- **Schedule** a report to be delivered to your email automatically — Daily, Weekly, or Monthly

---

## Getting Started

Open the application in your web browser. You will see the **Analytics Hub** screen with three report type options.

> If you see a red dot labelled **"Backend offline"** in the top-right corner, the system is not connected. Contact your IT administrator to start the backend server.

---

## Step-by-Step: Generate a Report Instantly

### Step 1 — Choose Your Report Type

On the home screen, click one of the three report cards:

| Report Card | What It Shows |
|-------------|---------------|
| 💰 **Sales Report** | Revenue, orders, product categories, and regional sales |
| 👤 **User Activity Report** | Who logged in, when, and what they did |
| 📦 **Inventory Report** | Current stock levels, low-stock alerts, warehouse totals |

Once you click a card, it will be highlighted with a blue border and a checkmark (✓). The **"Selected Report"** box below the cards will show your selection.

---

### Step 2 — Click "Generate Instant Report"

After selecting a report type, click the **⚡ Generate Instant Report** button.

> Both the **Generate Instant Report** and **Schedule Recurring Report** buttons are greyed out until you select a report type. They activate as soon as you click a card.

---

### Step 3 — Set Your Filters

You will be taken to the **Configure your filters** screen. The available filters depend on which report you selected:

#### Sales Report Filters

| Filter | Required? | Description |
|--------|-----------|-------------|
| **Start Date** | ✅ Yes | Beginning of the date range |
| **End Date** | ✅ Yes | End of the date range |
| **Category** | Optional | Focus on one product category (e.g. Electronics) |
| **Region** | Optional | Focus on one province (e.g. Western Province) |

#### User Activity Report Filters

| Filter | Required? | Description |
|--------|-----------|-------------|
| **Start Date** | ✅ Yes | Beginning of the date range |
| **End Date** | ✅ Yes | End of the date range |
| **User Name** | Optional | Filter activity for one specific user |
| **Activity Type** | Optional | Focus on a specific action (e.g. Login, Export PDF) |

#### Inventory Report Filters

| Filter | Required? | Description |
|--------|-----------|-------------|
| **Category** | Optional | Filter by product category |
| **Warehouse Location** | Optional | Filter by warehouse (e.g. Colombo Central WH) |

> For the Inventory Report, no date range is needed — the report always shows the **current stock snapshot**.

**Tip:** If you leave optional filters blank, the report will include **all** data (all categories, all regions, all warehouses).

---

### Step 4 — Click "Generate Report Now"

Once your filters are set, click the **⚡ Generate Report Now** button at the bottom of the screen.

A loading animation will appear while the system fetches and processes the data. This usually takes 2–5 seconds.

---

### Step 5 — Download Your Report

When the report is ready, you will see the **Results** screen with two download buttons:

| Button | What You Get |
|--------|-------------|
| 📄 **Download PDF** | A formatted PDF — ideal for printing and sharing |
| 📊 **Download Excel** | A spreadsheet — ideal for further analysis in Excel |

Click either button to download the file to your computer. You can download **both formats** from the same screen — they contain the same data.

The file will be saved automatically to your browser's default downloads folder with a name like:
- `sales_report_2026-06-24.pdf`
- `inventory_report_2026-06-24.xlsx`

---

### What If Something Goes Wrong?

If the report cannot be generated, you will see an error screen with a red ❌ icon and an explanation of what went wrong.

**Common causes and what to do:**

| Error Message | What It Means | What To Do |
|---------------|---------------|------------|
| "Cannot reach the Flask backend" | The system server is offline | Contact IT to restart the backend |
| "Start date must be before end date" | Your date range is invalid | Go back and correct the dates |
| "No data found for these filters" | The filters returned no results | Try a wider date range or remove optional filters |

Use the **🔧 Adjust Filters** button to go back and change your inputs, then try again.

---

## Step-by-Step: Schedule a Recurring Report

Instead of generating a report manually each time, you can set up automatic delivery on a schedule.

### Step 1 — Choose Your Report Type

From the home screen, click the report type card you want (Sales, User Activity, or Inventory).

### Step 2 — Click "Schedule Recurring Report"

Click the **📅 Schedule Recurring Report** button. You will be taken to the **Schedule** screen.

### Step 3 — Set Optional Filters *(optional)*

If you want every scheduled report to be filtered (e.g. only Western Province sales), you can set filters in the **Optional Filters** section at the top of the form.

If you leave these blank, each scheduled report will include all data at the time it runs.

### Step 4 — Fill In the Delivery Settings

| Field | Options | Description |
|-------|---------|-------------|
| **Frequency** | Daily / Weekly / Monthly | How often the report is sent |
| **Export Format** | PDF Document / Excel Spreadsheet | The file format to deliver |
| **Recipient Email** | Any valid email address | Where the report is sent |

### Step 5 — Click "Save Schedule"

Click the **💾 Save Schedule** button. If all fields are filled in correctly, you will see a green confirmation message showing:

- The report type
- The frequency
- The export format
- The recipient email
- The date of the **first dispatch**

**Example confirmation:**

> ✅ **Schedule saved!**
> Your first PDF Document will be delivered to finance@company.lk on next monday, 30 june 2026.

| | |
|-|-|
| **Report** | Sales Report |
| **Frequency** | Weekly |
| **Format** | PDF Document |
| **Recipient** | finance@company.lk |
| **First Dispatch** | Next Monday, 30 June |

---

## Navigating Between Screens

| Action | How To Do It |
|--------|-------------|
| Go back to the home screen | Click the **← Back** link at the top of any screen |
| Start a completely new report | Click **← New Report** on the results screen |
| Adjust your filters and regenerate | Click **🔧 Adjust Filters** on the results screen |
| Set up another schedule | Click **📅 Schedule Another** on the schedule confirmation |

The **progress bar** at the top of the page (Select → Configure → Results) shows where you are in the workflow.

---

## Frequently Asked Questions

**Q: Do I need to log in to use the tool?**
A: This version of the tool does not require a login. Contact your IT team if authentication has been added to your installation.

**Q: What date format should I use?**
A: Click on the date field and use the calendar picker that appears. You do not need to type the date manually.

**Q: How far back can I go with dates?**
A: The system includes data from when your organisation started using the platform. There is no hard limit — but very large date ranges may take longer to generate.

**Q: Can I download the same report in both PDF and Excel?**
A: Yes. From the Results screen, click both the PDF button and the Excel button. Each click generates and downloads the file independently.

**Q: What is the difference between PDF and Excel?**
A: **PDF** is formatted for reading, printing, and sharing in meetings. **Excel** is better if you need to filter, sort, add formulas, or do further analysis on the raw data.

**Q: I set a schedule — when will the first report arrive?**
A: The confirmation screen shows the exact first dispatch date:
- **Daily** — tomorrow
- **Weekly** — next Monday
- **Monthly** — the 1st of next month

**Q: Can I cancel or change a scheduled report?**
A: Contact your IT administrator or the Group 4 (Scheduling) team to modify or cancel existing schedules.

**Q: The download button spins but no file downloads. What should I do?**
A: The system may be having trouble connecting to the database. Wait a few seconds and try again. If the problem persists, contact IT.

---

## Glossary

| Term | Meaning |
|------|---------|
| **Report Type** | The kind of report: Sales, User Activity, or Inventory |
| **Filter** | A setting that narrows the report data (e.g. a date range or region) |
| **Export Format** | The file type for your download: PDF or Excel (.xlsx) |
| **Schedule** | An automatic recurring report sent to an email address |
| **Frequency** | How often a scheduled report runs: Daily, Weekly, or Monthly |
| **Backend** | The server software that processes your request and generates the file |
| **Recipient** | The email address that receives a scheduled report |
