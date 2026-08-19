import frappe
from frappe import _
from frappe.utils import today


@frappe.whitelist()
def get_sales_summary(from_date=None, to_date=None, department=None):
	"""Aggregated sales with optional filters."""
	frappe.has_permission("Sales Entry", "read", throw=True)
	conditions = ["docstatus = 1"]
	values = {}

	if from_date:
		conditions.append("dated >= %(from_date)s")
		values["from_date"] = from_date
	if to_date:
		conditions.append("dated <= %(to_date)s")
		values["to_date"] = to_date
	if department:
		conditions.append("department = %(department)s")
		values["department"] = department

	where = " AND ".join(conditions)
	return frappe.db.sql(f"""
		SELECT
			SUM(amount) AS total,
			SUM(CASE WHEN sale_type = 'Wet Stock' THEN amount ELSE 0 END) AS wet_stock,
			SUM(CASE WHEN sale_type = 'Other' THEN amount ELSE 0 END) AS other,
			COUNT(*) AS entry_count
		FROM `tabSales Entry`
		WHERE {where}
	""", values, as_dict=True)
