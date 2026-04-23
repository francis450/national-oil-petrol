import frappe


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 200},
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
        {"label": "Amount Paid", "fieldname": "amount_paid", "fieldtype": "Currency", "width": 150},
        {"label": "Balance", "fieldname": "balance", "fieldtype": "Currency", "width": 150},
        {"label": "Indicator", "fieldname": "indicator", "fieldtype": "Data", "width": 100},
    ]

    conditions = ["sc.docstatus < 2"]
    if filters.get("supplier"):
        conditions.append("sc.supplier = %(supplier)s")
    if filters.get("status"):
        conditions.append("sc.status = %(status)s")

    where = " AND ".join(conditions)

    rows = frappe.db.sql(
        f"""
        SELECT
            sc.supplier,
            SUM(sc.total_amount) AS total_amount,
            SUM(sc.amount_paid) AS amount_paid,
            SUM(sc.balance) AS balance
        FROM `tabSupplier Credit` sc
        WHERE {where}
        GROUP BY sc.supplier
        ORDER BY SUM(sc.balance) DESC
        """,
        filters,
        as_dict=True,
    )

    data = []
    for row in rows:
        row["indicator"] = "Open" if row["balance"] > 0 else "Settled"
        data.append(row)

    return columns, data
