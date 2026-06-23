"""
backend/models/sales_model.py
==============================
Data-access layer for the Sales Report.

Public API
----------
get_sales_data(filters: dict) -> pd.DataFrame
get_sales_summary(filters: dict) -> dict

filters keys (all optional)
----------------------------
    start_date  : str  "YYYY-MM-DD"
    end_date    : str  "YYYY-MM-DD"
    category    : str  product category name
    region      : str  region name
"""

import pandas as pd
from .db import get_connection


def _build_where(filters: dict) -> tuple[str, list]:
    """Return (WHERE clause, params list) for the given filters."""
    conditions, params = [], []

    if filters.get("start_date"):
        conditions.append("s.sale_date >= %s")
        params.append(filters["start_date"])

    if filters.get("end_date"):
        conditions.append("s.sale_date <= %s")
        params.append(filters["end_date"])

    if filters.get("category"):
        conditions.append("p.category = %s")
        params.append(filters["category"])

    if filters.get("region"):
        conditions.append("r.region_name = %s")
        params.append(filters["region"])

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


def get_sales_data(filters: dict | None = None) -> pd.DataFrame:
    """
    Return raw sales rows matching the given filters as a DataFrame.

    Columns: sale_id, product_name, category, sale_date,
             quantity_sold, unit_price, total_amount, region
    """
    filters = filters or {}
    where, params = _build_where(filters)

    sql = f"""
        SELECT
            s.sale_id,
            p.product_name,
            p.category,
            s.sale_date,
            s.quantity_sold,
            s.unit_price,
            s.total_amount,
            r.region_name   AS region
        FROM  sales         s
        JOIN  products      p ON p.product_id  = s.product_id
        JOIN  regions       r ON r.region_id   = s.region_id
        {where}
        ORDER BY s.sale_date DESC, s.sale_id DESC
    """

    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=tuple(params))
    finally:
        conn.close()

    # Ensure correct dtypes
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["total_amount"] = df["total_amount"].astype(float)
    df["unit_price"] = df["unit_price"].astype(float)
    return df


def get_sales_summary(filters: dict | None = None) -> dict:
    """
    Return aggregated KPIs + breakdowns for the Sales Report header.

    Returns
    -------
    {
        "total_revenue": float,
        "total_orders":  int,
        "total_units":   int,
        "by_product":    pd.DataFrame,   # product_name, total_qty, total_revenue
        "by_region":     pd.DataFrame,   # region, total_qty, total_revenue
        "by_category":   pd.DataFrame,   # category, total_qty, total_revenue
        "by_date":       pd.DataFrame,   # sale_date, total_revenue  (daily trend)
    }
    """
    df = get_sales_data(filters)

    if df.empty:
        empty_frame = pd.DataFrame()
        return {
            "total_revenue": 0.0,
            "total_orders":  0,
            "total_units":   0,
            "by_product":    empty_frame,
            "by_region":     empty_frame,
            "by_category":   empty_frame,
            "by_date":       empty_frame,
        }

    by_product = (
        df.groupby("product_name", as_index=False)
        .agg(total_qty=("quantity_sold", "sum"), total_revenue=("total_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
    )

    by_region = (
        df.groupby("region", as_index=False)
        .agg(total_qty=("quantity_sold", "sum"), total_revenue=("total_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
    )

    by_category = (
        df.groupby("category", as_index=False)
        .agg(total_qty=("quantity_sold", "sum"), total_revenue=("total_amount", "sum"))
        .sort_values("total_revenue", ascending=False)
    )

    by_date = (
        df.groupby("sale_date", as_index=False)
        .agg(total_revenue=("total_amount", "sum"))
        .sort_values("sale_date")
    )

    return {
        "total_revenue": float(df["total_amount"].sum()),
        "total_orders":  int(len(df)),
        "total_units":   int(df["quantity_sold"].sum()),
        "by_product":    by_product,
        "by_region":     by_region,
        "by_category":   by_category,
        "by_date":       by_date,
    }


def get_available_filters() -> dict:
    """Return distinct values for each Sales filter dropdown."""
    sql_categories = "SELECT DISTINCT category FROM products ORDER BY category"
    sql_regions = "SELECT region_name FROM regions ORDER BY region_name"

    conn = get_connection()
    try:
        categories = pd.read_sql(sql_categories, conn)["category"].tolist()
        regions = pd.read_sql(sql_regions,    conn)["region_name"].tolist()
    finally:
        conn.close()

    return {"categories": categories, "regions": regions}
