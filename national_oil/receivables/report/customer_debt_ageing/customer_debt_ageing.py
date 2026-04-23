import frappe
from frappe.utils import getdate, date_diff, today


def execute(filters=None):
    filters = filters or {}
    as_of = getdate(filters.get("as_of_date") or today())

    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": "0–30 Days", "fieldname": "range_0_30", "fieldtype": "Currency", "width": 130},
        {"label": "31–60 Days", "fieldname": "range_31_60", "fieldtype": "Currency", "width": 130},
        {"label": "61–90 Days", "fieldname": "range_61_90", "fieldtype": "Currency", "width": 130},
        {"label": "90+ Days", "fieldname": "range_90_plus", "fieldtype": "Currency", "width": 130},
        {"label": "Total Outstanding", "fieldname": "total", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "balance > 0 AND docstatus < 2"
    if filters.get("customer"):
        conditions += " AND customer = %(customer)s"

    debts = frappe.db.sql(
        f"SELECT customer, dated, balance FROM `tabCustomer Debt` WHERE {conditions}",
        filters,
        as_dict=True,
    )

    ageing = {}
    for d in debts:
        c = d.customer
        if c not in ageing:
            ageing[c] = {"customer": c, "range_0_30": 0, "range_31_60": 0, "range_61_90": 0, "range_90_plus": 0}
        days = date_diff(as_of, getdate(d.dated))
        if days <= 30:
            ageing[c]["range_0_30"] += d.balance
        elif days <= 60:
            ageing[c]["range_31_60"] += d.balance
        elif days <= 90:
            ageing[c]["range_61_90"] += d.balance
        else:
            ageing[c]["range_90_plus"] += d.balance

    data = []
    for row in sorted(ageing.values(), key=lambda x: x["range_90_plus"] + x["range_61_90"], reverse=True):
        row["total"] = row["range_0_30"] + row["range_31_60"] + row["range_61_90"] + row["range_90_plus"]
        data.append(row)

    return columns, data
