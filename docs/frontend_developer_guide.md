# Frontend Developer Guide

> **For Group 3 (Frontend) and Group 5 (Documentation & Testing)**
> This document describes the complete technical structure of the Custom Report Generator frontend — its file layout, screen flow, JavaScript API, and how it connects to the Flask backend.

---

## Quick Start

```bash
# 1. Start the Flask backend (required for API calls)
python backend/app.py
# Backend runs at http://127.0.0.1:5000

# 2. Serve the frontend (from the project root)
python -m http.server 8080 --directory frontend
# Open http://localhost:8080 in your browser
```

> You can also open `frontend/index.html` directly in a browser (double-click),  
> but note that relative `fetch()` calls still require the Flask backend to be running.

---

## File Structure

```
frontend/
├── index.html          # All 4 application screens (single-page app)
├── css/
│   └── styles.css      # Full design system — variables, layout, components
└── js/
    └── app.js          # All application logic, state, and API communication
```

---

## Screen Flow

```
Screen 1 ──[Generate]──► Screen 2 ──[Generate Report Now]──► Screen 4
(Select)                 (Filters)                           (Download)
   │
   └──[Schedule]────────► Screen 3 ──[Save Schedule]──► Confirmation
                          (Schedule)
```

| Screen | ID   | Purpose |
|--------|------|---------|
| Screen 1 | `#s1` | Pick a report type (Sales / User Activity / Inventory) |
| Screen 2 | `#s2` | Set filters specific to that report type, then generate |
| Screen 3 | `#s3` | Set up a recurring schedule with delivery settings |
| Screen 4 | `#s4` | Download the generated report as PDF or Excel |

Navigation is handled entirely by the `goTo(n)` function in `app.js`. No page reloads occur.

---

## CSS Design System (`css/styles.css`)

### CSS Custom Properties (Variables)

| Variable | Value | Usage |
|----------|-------|-------|
| `--blue` | `#2a5298` | Primary brand colour |
| `--teal` | `#1a8a6e` | Secondary brand colour |
| `--teal-lt` | `#22b98e` | Active highlights, nav dots |
| `--gradient` | blue → teal | Buttons, card accents |
| `--card` | `#ffffff` | White content surfaces |
| `--error` | `#dc2626` | Error states |
| `--success` | `#059669` | Success states |
| `--t-med` | `0.24s ease` | Standard transition speed |

### Key CSS Classes

| Class | Description |
|-------|-------------|
| `.screen` | Hidden screen container. Add `.is-active` to show it. |
| `.card` | White rounded content surface with shadow |
| `.btn-grad` | Gradient (blue→teal) primary button |
| `.btn-ghost` | Outline secondary button |
| `.btn-dl-pdf` | Red gradient — PDF download button |
| `.btn-dl-xls` | Green gradient — Excel download button |
| `.alert` | Hidden alert banner. Add `.show` to display. |
| `.alert-err` | Red error variant of `.alert` |
| `.alert-ok` | Green success variant of `.alert` |
| `.rtype-card` | Report type selector card |
| `.rtype-card.is-selected` | Selected state of a report type card |
| `.filter-panel` | Container for one report type's filter fields |
| `.sched-filters` | Optional filter section inside the Schedule screen |
| `.sched-confirm` | Schedule confirmation panel. Add `.show` to display. |
| `.loading-overlay` | Full-screen loading overlay. Add `.show` to display. |
| `.toast` | Individual toast notification element |
| `.btn-spin` | CSS spinner animation inside buttons |

---

## JavaScript Application (`js/app.js`)

### Configuration

```javascript
const API_BASE = 'http://127.0.0.1:5000';

const ENDPOINTS = {
  generateReport: `${API_BASE}/api/generate-report`,
  filters:        (type) => `${API_BASE}/api/filters/${type}`,
  health:         `${API_BASE}/api/health`,
};
```

To change the backend URL, edit only `API_BASE`.

---

### Application State

```javascript
const State = {
  reportKey:     null,   // 'sales' | 'user_activity' | 'inventory'
  reportLabel:   null,   // Human-readable label e.g. "Sales Report"
  reportIcon:    null,   // Emoji icon e.g. "💰"
  filtersCache:  {},     // { [reportKey]: filterData } — cached from /api/filters/<type>
  lastFilters:   {},     // Filter payload used in the last generate call
  isOnline:      false,  // Whether the Flask backend responded to /api/health
};
```

All mutable values live in `State`. Access them directly for debugging in the browser console.

---

### Public Functions Reference

#### Navigation

| Function | Description |
|----------|-------------|
| `goTo(n)` | Navigate to screen `n` (1–4). Updates nav step pills. |
| `gotoFilters()` | Navigate to Screen 2. Sets context chip and shows correct filter panel. |
| `gotoSchedule()` | Navigate to Screen 3. Resets the schedule form. |
| `gotoFiltersFromResult()` | Return to Screen 2 from Screen 4, preserving filter state. |

#### Screen 1

| Function | Description |
|----------|-------------|
| `pickReport(card)` | Called `onclick` of a report type card. Stores selection in `State`. |

#### Screen 2 — Filters & Generate

| Function | Description |
|----------|-------------|
| `handleGenerate()` | Validates inputs, checks backend health, then calls `prepareResultScreen()` and navigates to Screen 4. |
| `collectPayload(exportFormat)` | Reads all filter field values and builds the Flask-compatible JSON payload. Saves filters to `State.lastFilters`. |
| `validate(payload)` | Returns `{ ok, msg }`. Sales and User Activity reports require both `start_date` and `end_date`. |
| `loadFilterOptions(reportType)` | Calls `GET /api/filters/<type>`. Caches result in `State.filtersCache`. |
| `populateFilterDropdowns(type, filters)` | Fills `<select>` elements with API-sourced values. Falls back to static HTML options. |

#### Screen 3 — Schedule

| Function | Description |
|----------|-------------|
| `handleSaveSchedule()` | Validates frequency, format, and email. Calculates first dispatch date. Shows confirmation panel. |
| `updateScheduleFilters()` | Shows the correct filter sub-panel for the current report type. |
| `collectScheduleFilters()` | Reads schedule-screen filter values into the backend payload format. |
| `clearScheduleFilters()` | Clears all filter input fields on the schedule screen. |

#### Screen 4 — Download

| Function | Description |
|----------|-------------|
| `prepareResultScreen()` | Populates metadata, resets download buttons, shows success state. |
| `triggerDownload(fmt)` | Calls `POST /api/generate-report` with `fmt = 'pdf' \| 'excel'`. Downloads the response blob as a file. |

#### Utility Helpers

| Function | Description |
|----------|-------------|
| `v(id)` | Returns trimmed value of a form field by ID. Returns `''` if not found. |
| `setVal(id, val)` | Sets a field's value by ID. |
| `setText(id, text)` | Sets an element's `textContent` by ID. |
| `show(id)` / `hide(id)` | Show or hide an element by ID. |
| `addClass(id, cls)` / `removeClass(id, cls)` | Toggle a CSS class on an element. |
| `showAlert(bannerId, bodyId, msg)` | Show an alert banner with a message. Scrolls it into view. |
| `hideAlert(bannerId)` | Hide an alert banner. |
| `showToast(message, type, duration)` | Display a temporary toast notification (`'success' \| 'error' \| 'info'`). |
| `showLoading(text, sub)` | Display the full-screen loading overlay. |
| `hideLoading()` | Hide the loading overlay. |
| `setGenBtnLoading(loading)` | Toggle the Generate button between its loading spinner and normal label. |
| `checkHealth()` | Calls `GET /api/health`. Updates `State.isOnline` and the nav status dot. |

---

### Backend API Connection

The frontend connects to three endpoints:

#### `POST /api/generate-report`

Called by `triggerDownload(fmt)` each time a download button is clicked.

```javascript
// Exact payload shape sent to Flask
{
  "report_type":   "sales",          // required
  "export_format": "pdf",            // "pdf" | "excel"
  "filters": {
    "start_date":  "2026-06-01",     // sales, user_activity
    "end_date":    "2026-06-30",     // sales, user_activity
    "category":    "Electronics",    // sales, inventory
    "region":      "Western Province", // sales only
    "username":    "ashan.perera",   // user_activity only
    "activity_type": "Login",        // user_activity only
    "warehouse_location": "Colombo Central WH" // inventory only
  }
}
```

Response: Binary file blob (`.xlsx` or `.pdf`) downloaded directly by the browser.

#### `GET /api/filters/<report_type>`

Called by `loadFilterOptions()` when entering Screen 2. Response is cached in `State.filtersCache`.

```javascript
// Example response for 'sales'
{
  "report_type": "sales",
  "filters": {
    "categories": ["Clothing", "Electronics", ...],
    "regions":    ["Central Province", "Western Province", ...]
  }
}
```

#### `GET /api/health`

Called on startup and every 30 seconds. Updates the nav status indicator (🟢 / 🔴).

---

### Filter Field ID Reference

| Report Type | Field | HTML Element ID | Backend Key |
|-------------|-------|-----------------|-------------|
| Sales | Start Date | `s-start` | `start_date` |
| Sales | End Date | `s-end` | `end_date` |
| Sales | Category | `s-cat` | `category` |
| Sales | Region | `s-region` | `region` |
| User Activity | Start Date | `ua-start` | `start_date` |
| User Activity | End Date | `ua-end` | `end_date` |
| User Activity | User Name | `ua-user` | `username` |
| User Activity | Activity Type | `ua-type` | `activity_type` |
| Inventory | Category | `inv-cat` | `category` |
| Inventory | Warehouse | `inv-wh` | `warehouse_location` |

Schedule screen filter fields follow the same pattern with a `sc-` prefix (e.g. `sc-s-start`, `sc-ua-type`, `sc-inv-wh`).

---

## Adding a New Report Type

To add a new report type (e.g. "Financial Report"):

1. **`index.html`** — Add a new `.rtype-card` button in `#s1` with `data-key`, `data-lbl`, `data-icon`.
2. **`index.html`** — Add a new `<div id="fg-financial" class="filter-panel">` in `#s2` with the relevant filter fields.
3. **`index.html`** — Add a matching `<div id="sched-fg-financial">` inside `#s3 .sched-filters`.
4. **`js/app.js`** — Add a new `if (key === 'financial')` block in `collectPayload()` and `collectScheduleFilters()`.
5. **`js/app.js`** — Add a new `if (reportType === 'financial')` block in `populateFilterDropdowns()`.
6. **Backend** — Add the new report type to the Flask API (Group 2's responsibility).

---

## Responsive Breakpoints

| Breakpoint | Changes Applied |
|------------|-----------------|
| `≤ 660px` | Nav progress pills hidden; single-column layout for cards, action row, date pair, download row |
| `≤ 480px` | Report type cards forced to single column |

---

## Browser Compatibility

| Feature | Notes |
|---------|-------|
| `fetch()` | All modern browsers. No polyfill required. |
| `AbortSignal.timeout()` | Chrome 103+, Firefox 100+, Safari 16+. Used for health-check and filter-load timeouts. |
| CSS `backdrop-filter` | Requires `-webkit-` prefix for Safari (included). |
| CSS `grid` | All modern browsers. |
| `Blob` + `createObjectURL` | All modern browsers. Used for file download. |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Nav dot shows 🔴 "Backend offline" | Flask is not running | Run `python backend/app.py` |
| Filter dropdowns don't populate from DB | Backend offline or DB not seeded | Check Flask terminal output; run `mysql ... < database/seed_data.sql` |
| CORS error in browser console | Browser blocked the cross-origin request | Ensure `flask-cors` is installed and `CORS(app)` is called in `app.py` |
| Downloaded file won't open | Backend returned an error as a 200 response | Check Flask terminal for exceptions; verify DB credentials in `.env` |
| "No report selected" on Generate click | Report type card not clicked | Click one of the three report type cards first |
| Date validation error | Start date is after end date | Adjust the date range so start ≤ end |
