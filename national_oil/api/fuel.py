import frappe
from frappe import _
from frappe.utils import cint, flt, today


@frappe.whitelist()
def get_fuel_stock():
	"""Current stock levels per fuel product."""
	return frappe.db.sql("""
		SELECT p.name, p.product_name, p.quantity, ft.unit_of_measure
		FROM `tabProduct` p
		LEFT JOIN `tabFuel Type` ft ON ft.name = p.fuel_type
		WHERE p.is_fuel = 1
		ORDER BY p.product_name
	""", as_dict=True)


@frappe.whitelist()
def get_current_prices():
	"""Latest fuel prices per fuel type (most recent effective_date)."""
	return frappe.db.sql("""
		SELECT fp.*
		FROM `tabFuel Price` fp
		INNER JOIN (
			SELECT fuel_type, MAX(effective_date) AS max_date
			FROM `tabFuel Price`
			GROUP BY fuel_type
		) latest ON fp.fuel_type = latest.fuel_type AND fp.effective_date = latest.max_date
		ORDER BY fp.fuel_type
	""", as_dict=True)


@frappe.whitelist()
def get_recent_pump_readings(limit_page_length=20):
	"""Return recent pump readings plus today's aggregate throughput."""
	limit_page_length = min(max(cint(limit_page_length or 20), 1), 100)
	rows = frappe.get_all(
		"Pump Reading",
		fields=[
			"name",
			"dated",
			"pump_number",
			"fuel_type",
			"opening_reading",
			"closing_reading",
			"variance",
			"attendant",
			"department",
		],
		order_by="dated desc, modified desc",
		limit_page_length=limit_page_length,
	)

	today_rows = frappe.get_all(
		"Pump Reading",
		fields=["pump_number", "variance"],
		filters={"dated": today()},
		limit_page_length=500,
	)

	return {
		"count": len(rows),
		"rows": rows,
		"today": {
			"reading_count": len(today_rows),
			"throughput": sum(flt(row.get("variance")) for row in today_rows),
		},
	}
