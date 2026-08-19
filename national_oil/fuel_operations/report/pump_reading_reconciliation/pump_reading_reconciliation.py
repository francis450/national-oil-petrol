import frappe


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Shift Assignment", "fieldname": "shift", "fieldtype": "Link", "options": "Shift Assignment", "width": 150},
        {"label": "Attendant", "fieldname": "attendant", "fieldtype": "Data", "width": 150},
        {"label": "Shift Type", "fieldname": "shift_type", "fieldtype": "Link", "options": "Shift Type", "width": 120},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": "Reconciliation Status", "fieldname": "reconciliation_status", "fieldtype": "Data", "width": 130},
        {"label": "Total Expected Sales", "fieldname": "total_expected_sales", "fieldtype": "Currency", "width": 150},
        {"label": "Sales Entry Total", "fieldname": "sales_entry_total", "fieldtype": "Currency", "width": 150},
        {"label": "Variance", "fieldname": "variance", "fieldtype": "Currency", "width": 120},
        {"label": "Closed At", "fieldname": "closed_at", "fieldtype": "Datetime", "width": 160},
    ]

    conditions = ["1=1"]
    if filters.get("from_date"):
        conditions.append("sa.start_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("sa.start_date <= %(to_date)s")
    if filters.get("reconciliation_status"):
        conditions.append("sa.reconciliation_status = %(reconciliation_status)s")

    where = " AND ".join(conditions)

    rows = frappe.db.sql(
        f"""
        SELECT
            sa.name AS shift,
            sa.employee_name AS attendant,
            sa.shift_type AS shift_type,
            sa.start_date AS start_date,
            sa.reconciliation_status AS reconciliation_status,
            sa.total_expected_sales AS total_expected_sales,
            sa.closed_at AS closed_at,
            COALESCE(se.sales_entry_total, 0) AS sales_entry_total
        FROM `tabShift Assignment` sa
        LEFT JOIN (
            SELECT shift, SUM(amount) AS sales_entry_total
            FROM `tabSales Entry`
            WHERE docstatus = 1 AND shift IS NOT NULL AND shift != ''
            GROUP BY shift
        ) se ON se.shift = sa.name
        WHERE {where}
        ORDER BY sa.start_date DESC, sa.name
        """,
        filters,
        as_dict=True,
    )

    data = []
    for row in rows:
        row["variance"] = (row.get("sales_entry_total") or 0) - (row.get("total_expected_sales") or 0)
        if row["variance"] < 0:
            row["variance_color"] = "red"
        data.append(row)

    return columns, data
