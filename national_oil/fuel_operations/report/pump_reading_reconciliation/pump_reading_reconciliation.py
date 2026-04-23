import frappe


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Date", "fieldname": "dated", "fieldtype": "Date", "width": 100},
        {"label": "Pump", "fieldname": "pump_number", "fieldtype": "Data", "width": 100},
        {"label": "Fuel Type", "fieldname": "fuel_type", "fieldtype": "Link", "options": "Fuel Type", "width": 120},
        {"label": "Opening (L)", "fieldname": "opening_reading", "fieldtype": "Float", "width": 120},
        {"label": "Closing (L)", "fieldname": "closing_reading", "fieldtype": "Float", "width": 120},
        {"label": "Dispensed (L)", "fieldname": "dispensed", "fieldtype": "Float", "width": 130},
        {"label": "Variance (L)", "fieldname": "variance", "fieldtype": "Float", "width": 120},
        {"label": "Attendant", "fieldname": "attendant", "fieldtype": "Link", "options": "NO Employee", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 140},
    ]

    conditions = ["1=1"]
    if filters.get("from_date"):
        conditions.append("dated >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("dated <= %(to_date)s")
    if filters.get("pump_number"):
        conditions.append("pump_number = %(pump_number)s")
    if filters.get("fuel_type"):
        conditions.append("fuel_type = %(fuel_type)s")

    where = " AND ".join(conditions)

    rows = frappe.db.sql(
        f"""
        SELECT
            dated, pump_number, fuel_type,
            opening_reading, closing_reading,
            (closing_reading - opening_reading) AS dispensed,
            variance, attendant, department
        FROM `tabPump Reading`
        WHERE {where}
        ORDER BY dated DESC, pump_number
        """,
        filters,
        as_dict=True,
    )

    data = []
    for row in rows:
        if (row.get("variance") or 0) < 0:
            row["variance_color"] = "red"
        data.append(row)

    return columns, data
