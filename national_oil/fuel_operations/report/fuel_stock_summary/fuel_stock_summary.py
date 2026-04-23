import frappe


def execute(filters=None):
    filters = filters or {}

    columns = [
        {"label": "Product", "fieldname": "product_name", "fieldtype": "Data", "width": 200},
        {"label": "Fuel Type", "fieldname": "fuel_type", "fieldtype": "Link", "options": "Fuel Type", "width": 130},
        {"label": "Current Stock", "fieldname": "quantity", "fieldtype": "Float", "width": 130},
        {"label": "Unit", "fieldname": "unit_of_measure", "fieldtype": "Data", "width": 80},
        {"label": "Buying Price", "fieldname": "buying_price", "fieldtype": "Currency", "width": 130},
        {"label": "Retail Price", "fieldname": "selling_price", "fieldtype": "Currency", "width": 130},
        {"label": "Wholesale Price", "fieldname": "selling_price_wholesale", "fieldtype": "Currency", "width": 150},
        {"label": "Stock Value", "fieldname": "stock_value", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "is_fuel = 1"
    if filters.get("fuel_type"):
        conditions += " AND fuel_type = %(fuel_type)s"

    rows = frappe.db.sql(
        f"""
        SELECT product_name, fuel_type, quantity, unit_of_measure,
               buying_price, selling_price, selling_price_wholesale
        FROM `tabProduct`
        WHERE {conditions}
        ORDER BY fuel_type, product_name
        """,
        filters,
        as_dict=True,
    )

    data = []
    for row in rows:
        row["stock_value"] = (row.get("quantity") or 0) * (row.get("buying_price") or 0)
        data.append(row)

    return columns, data
