"""
backend/models/inventory_model.py
==================================
Data-access layer for the Inventory Report.

Public API
----------
get_inventory_data(filters: dict) -> pd.DataFrame
get_inventory_summary(filters: dict) -> dict

filters keys (all optional)
----------------------------
    category            : str  product category name
    warehouse_location  : str  warehouse location
"""

import pandas as pd
from .db import get_connection


def _build_where(filters: dict) -> tuple[str, list]:
    conditions, params = [], []

    if filters.get("category"):
        conditions.append("p.category = %s")
        params.append(filters["category"])

    if filters.get("warehouse_location"):
        conditions.append("w.location = %s")
        params.append(filters["warehouse_location"])

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


def get_inventory_data(filters: dict | None = None) -> pd.DataFrame:
    """
    Return current inventory rows matching filters.

    Columns: product_id, product_name, category, unit_price,
             reorder_level, warehouse_name, warehouse_location,
             current_stock, stock_status
    """
    filters = filters or {}
    where, params = _build_where(filters)

    sql = f"""
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            p.unit_price,
            p.reorder_level,
            w.warehouse_name,
            w.location         AS warehouse_location,
            i.current_stock,
            CASE
                WHEN i.current_stock = 0                      THEN 'Out of Stock'
                WHEN i.current_stock <= p.reorder_level       THEN 'Low Stock'
                WHEN i.current_stock <= p.reorder_level * 1.5 THEN 'Reorder Soon'
                ELSE 'In Stock'
            END                AS stock_status
        FROM  inventory  i
        JOIN  products   p ON p.product_id   = i.product_id
        JOIN  warehouses w ON w.warehouse_id = i.warehouse_id
        {where}
        ORDER BY stock_status, p.category, p.product_name
    """

    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=tuple(params))
    finally:
        conn.close()

    df["unit_price"] = df["unit_price"].astype(float)
    # Computed: stock value at current price
    df["stock_value"] = (df["current_stock"] * df["unit_price"]).round(2)
    return df


def get_inventory_summary(filters: dict | None = None) -> dict:
    """
    Return aggregated inventory KPIs + breakdowns.

    Returns
    -------
    {
        "total_products":       int,
        "total_stock_units":    int,
        "total_stock_value":    float,
        "out_of_stock_count":   int,
        "low_stock_count":      int,
        "low_stock_items":      pd.DataFrame,  # products at/below reorder level
        "by_category":          pd.DataFrame,  # category, total_qty, total_value
        "by_warehouse":         pd.DataFrame,  # warehouse, total_qty, total_value
        "by_status":            pd.DataFrame,  # stock_status, count
    }
    """
    df = get_inventory_data(filters)

    if df.empty:
        empty = pd.DataFrame()
        return {
            "total_products":     0,
            "total_stock_units":  0,
            "total_stock_value":  0.0,
            "out_of_stock_count": 0,
            "low_stock_count":    0,
            "low_stock_items":    empty,
            "by_category":        empty,
            "by_warehouse":       empty,
            "by_status":          empty,
        }

    low_stock = df[df["stock_status"].isin(
        ["Low Stock", "Out of Stock"])].copy()

    by_category = (
        df.groupby("category", as_index=False)
        .agg(total_units=("current_stock", "sum"),
             total_value=("stock_value", "sum"))
        .sort_values("total_value", ascending=False)
    )

    by_warehouse = (
        df.groupby("warehouse_name", as_index=False)
        .agg(total_units=("current_stock", "sum"),
             total_value=("stock_value", "sum"),
             product_count=("product_id", "nunique"))
        .sort_values("total_units", ascending=False)
    )

    by_status = (
        df.groupby("stock_status", as_index=False)
        .agg(count=("product_id", "count"))
    )

    return {
        "total_products":     int(df["product_id"].nunique()),
        "total_stock_units":  int(df["current_stock"].sum()),
        "total_stock_value":  round(float(df["stock_value"].sum()), 2),
        "out_of_stock_count": int((df["stock_status"] == "Out of Stock").sum()),
        "low_stock_count":    int((df["stock_status"] == "Low Stock").sum()),
        "low_stock_items":    low_stock,
        "by_category":        by_category,
        "by_warehouse":       by_warehouse,
        "by_status":          by_status,
    }


def get_available_filters() -> dict:
    """Return distinct values for each Inventory filter dropdown."""
    sql_categories = "SELECT DISTINCT category FROM products ORDER BY category"
    sql_warehouse_locations = "SELECT location FROM warehouses ORDER BY location"

    conn = get_connection()
    try:
        categories = pd.read_sql(sql_categories, conn)["category"].tolist()
        warehouse_locations = pd.read_sql(sql_warehouse_locations, conn)[
            "location"].tolist()
    finally:
        conn.close()

    return {"categories": categories, "warehouse_locations": warehouse_locations}
