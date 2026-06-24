# Backend API & Function Reference

> **For Group 3 (Frontend) and Group 4 (Scheduler/Integration)**  
> This document describes every public function and HTTP endpoint exposed by the Group 2 backend.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure database  (copy .env.example → .env and fill in your MySQL credentials)
cp .env.example .env

# 3. Create and seed the database
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed_data.sql

# 4. Run the backend
python -m backend.app
# Server starts at http://localhost:5000
```

---

## Direct Python Function (Group 4 / Scheduler)

```python
from backend.app import generate_report
```

### `generate_report(report_type, filters=None, export_format="excel") → io.BytesIO`

Generates a report entirely in-process and returns a ready-to-save/stream `BytesIO` object.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_type` | `str` | ✅ | `"sales"` \| `"user_activity"` \| `"inventory"` |
| `filters` | `dict` | ❌ | Filter key/value pairs (see filter keys below) |
| `export_format` | `str` | ❌ | `"excel"` (default) \| `"pdf"` |

**Returns:** `io.BytesIO` with seek position at 0.

**Raises:** `ValueError` for invalid `report_type` or `export_format`.

#### Example — save a Sales PDF for June 2026

```python
from backend.app import generate_report

buf = generate_report(
    report_type="sales",
    filters={
        "start_date": "2026-06-01",
        "end_date":   "2026-06-30",
        "region":     "Western Province",
    },
    export_format="pdf",
)

with open("sales_june_2026.pdf", "wb") as f:
    f.write(buf.read())
```

#### Example — email an Inventory Excel report

```python
import smtplib
from email.mime.base import MIMEBase
from backend.app import generate_report

buf = generate_report("inventory", export_format="excel")
# attach buf.read() as attachment in your email client
```

---

## HTTP API Endpoints (Group 3 / Frontend)

Base URL: `http://localhost:5000`

---

### `GET /api/health`

Simple health-check. Returns `200 OK` if the server is running.

```json
{ "status": "ok" }
```

---

### `GET /api/report-types`

Returns metadata for all supported report types — useful for building the UI dynamically.

**Response:**
```json
{
  "report_types": [
    {
      "id":          "sales",
      "label":       "Sales Report",
      "description": "Revenue, orders, and regional/product breakdowns.",
      "filter_keys": ["start_date", "end_date", "category", "region"],
      "formats":     ["excel", "pdf"]
    },
    {
      "id":          "user_activity",
      "label":       "User Activity Report",
      "description": "Login frequency, session stats, and activity breakdown.",
      "filter_keys": ["start_date", "end_date", "username", "activity_type"],
      "formats":     ["excel", "pdf"]
    },
    {
      "id":          "inventory",
      "label":       "Inventory Report",
      "description": "Stock levels, low-stock alerts, and warehouse breakdown.",
      "filter_keys": ["category", "warehouse_location"],
      "formats":     ["excel", "pdf"]
    }
  ]
}
```

---

### `GET /api/filters/<report_type>`

Returns the available dropdown values for each filter field.  
Call this endpoint to populate filter dropdowns in the UI.

**URL parameters:**

| Parameter | Values |
|-----------|--------|
| `report_type` | `sales` \| `user_activity` \| `inventory` |

**Example:** `GET /api/filters/sales`

```json
{
  "report_type": "sales",
  "filters": {
    "start_date": "All data on or after the start date",
    "end_date":   "All data up to the end date",
    "categories": ["Clothing", "Electronics", "Food & Beverages", "Furniture", "Health & Beauty", "Sports", "Stationery"],
    "regions":    ["Central Province", "Eastern Province", "Northern Province", "North Western Province", "Sabaragamuwa Province", "Southern Province", "Western Province"]
  }
}
```

**Example:** `GET /api/filters/inventory`

```json
{
  "report_type": "inventory",
  "filters": {
    "categories": ["Clothing", "Electronics", ...],
    "warehouse_locations": ["Batticaloa, Eastern Province", "Colombo 10, Western Province", ...]
  }
}
```

---

### `POST /api/generate-report`

Generates and downloads a report file.

**Request body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_type` | `string` | ✅ | `"sales"` \| `"user_activity"` \| `"inventory"` |
| `export_format` | `string` | ❌ | `"excel"` (default) \| `"pdf"` |
| `filters` | `object` | ❌ | Filter key/value pairs |

**Response:** Binary file download (`.xlsx` or `.pdf`) with `Content-Disposition: attachment`.

#### Filter keys reference

| Report Type | Filter Key | Type | Example Value |
|-------------|-----------|------|---------------|
| `sales` | `start_date` | `string` | `"2026-06-01"` |
| `sales` | `end_date` | `string` | `"2026-06-30"` |
| `sales` | `category` | `string` | `"Electronics"` |
| `sales` | `region` | `string` | `"Western Province"` |
| `user_activity` | `start_date` | `string` | `"2026-06-01"` |
| `user_activity` | `end_date` | `string` | `"2026-06-30"` |
| `user_activity` | `username` | `string` | `"ashan.perera"` |
| `user_activity` | `activity_type` | `string` | `"Login"` |
| `inventory` | `category` | `string` | `"Electronics"` |
| `inventory` | `warehouse_location` | `string` | `"Colombo 10, Western Province"` |

#### Example — Sales Excel (June 2026, Electronics, Western Province)

```json
POST /api/generate-report
Content-Type: application/json

{
  "report_type":   "sales",
  "export_format": "excel",
  "filters": {
    "start_date": "2026-06-01",
    "end_date":   "2026-06-30",
    "category":   "Electronics",
    "region":     "Western Province"
  }
}
```

#### Example — Inventory PDF (no filters = all warehouses)

```json
POST /api/generate-report
Content-Type: application/json

{
  "report_type":   "inventory",
  "export_format": "pdf",
  "filters": {}
}
```

#### Error responses

```json
{ "error": "Missing required field: 'report_type'" }          // 400
{ "error": "Invalid report_type 'xyz'. Supported values: ..." } // 400
{ "error": "Server error: <details>" }                         // 500
```

---

## Data Model Summary (for context)

### Sales Report columns

| Column | Type | Description |
|--------|------|-------------|
| `sale_id` | int | Unique transaction ID |
| `product_name` | str | Product name |
| `category` | str | Product category |
| `sale_date` | date | Date of sale |
| `quantity_sold` | int | Units sold |
| `unit_price` | float | Price per unit (LKR) |
| `total_amount` | float | `quantity × price` |
| `region` | str | Sales region |

### User Activity Report columns

| Column | Type | Description |
|--------|------|-------------|
| `activity_id` | int | Activity record ID |
| `user_id` | int | User ID |
| `username` | str | Login username |
| `full_name` | str | Display name |
| `login_date` | date | Date of activity |
| `login_time` | str | Time of activity (HH:MM:SS) |
| `activity_type` | str | e.g., Login, Export PDF |
| `session_duration` | int | Minutes (NULL for non-login types) |
| `ip_address` | str | Client IP |

### Inventory Report columns

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | int | Product ID |
| `product_name` | str | Product name |
| `category` | str | Product category |
| `unit_price` | float | Current unit price (LKR) |
| `reorder_level` | int | Minimum stock threshold |
| `warehouse_name` | str | Warehouse name |
| `warehouse_location` | str | Physical location |
| `current_stock` | int | Units in stock |
| `stock_value` | float | `current_stock × unit_price` |
| `stock_status` | str | `In Stock` / `Reorder Soon` / `Low Stock` / `Out of Stock` |

---

## File Structure

```
backend/
├── app.py                          # Flask app factory + generate_report() helper
├── models/
│   ├── db.py                       # SQLAlchemy connection pool
│   ├── sales_model.py              # Sales data + summary + filter values
│   ├── activity_model.py           # Activity data + summary + filter values
│   ├── inventory_model.py          # Inventory data + summary + filter values
│   └── __init__.py                 # Public exports
├── routes/
│   └── report_routes.py            # All /api/* Flask routes
└── templates_engine/
    ├── excel_generator.py          # OpenPyXL → .xlsx
    └── pdf_generator.py            # ReportLab → .pdf

database/
├── schema.sql                      # MySQL DDL (8 tables)
└── seed_data.sql                   # Mock data (7 regions, 35 products, 5 warehouses,
                                    #            10 users, ~400 sales, 85 activity rows)
```
