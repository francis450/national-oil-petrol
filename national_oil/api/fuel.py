import frappe
from frappe import _


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
