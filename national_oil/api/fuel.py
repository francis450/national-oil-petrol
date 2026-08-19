import frappe
from frappe import _
from frappe.utils import cint, flt, today


@frappe.whitelist()
def get_fuel_stock():
	"""Current stock levels per fuel product."""
	frappe.has_permission("Product", "read", throw=True)
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
	frappe.has_permission("Fuel Price", "read", throw=True)
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
	frappe.has_permission("Pump Reading", "read", throw=True)
	limit_page_length = min(max(cint(limit_page_length or 20), 1), 100)
	rows = frappe.get_all(
		"Pump Reading",
		fields=[
			"name",
			"dated",
			"shift",
			"nozzle_no",
			"pump_number",
			"pump_no",
			"fuel_type",
			"opening_reading",
			"closing_reading",
			"variance",
			"unit_price",
			"expected_sales_amount",
			"attendant",
			"department",
		],
		order_by="dated desc, modified desc",
		limit_page_length=limit_page_length,
	)

	today_rows = frappe.get_all(
		"Pump Reading",
		fields=["pump_number", "variance", "expected_sales_amount"],
		filters={"dated": today()},
		limit_page_length=500,
	)

	return {
		"count": len(rows),
		"rows": rows,
		"today": {
			"reading_count": len(today_rows),
			"throughput": sum(flt(row.get("variance")) for row in today_rows),
			"expected_sales": sum(flt(row.get("expected_sales_amount")) for row in today_rows),
		},
	}


@frappe.whitelist()
def get_nozzle_defaults(nozzle_no):
	"""Return the pump/fuel-type defaults for a nozzle number (1-13)."""
	from national_oil.fuel_operations.doctype.pump_reading.pump_reading import (
		get_nozzle_defaults as _get_nozzle_defaults,
	)

	return _get_nozzle_defaults(nozzle_no)


@frappe.whitelist()
def get_my_shift_context():
	"""Return the current attendant's linked employee, open Shift Assignment, and in-progress readings."""
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if not employee:
		return {"employee": None, "shift": None, "open_readings": []}

	shift_name = frappe.db.get_value(
		"Shift Assignment",
		{
			"employee": employee,
			"docstatus": ["<", 2],
			"status": "Active",
			"reconciliation_status": ["!=", "Closed"],
			"start_date": ["<=", today()],
		},
		"name",
		order_by="start_date desc",
	)
	shift = frappe.get_doc("Shift Assignment", shift_name).as_dict() if shift_name else None

	open_readings = []
	if shift_name:
		open_readings = frappe.get_all(
			"Pump Reading",
			filters={"shift": shift_name, "docstatus": 0},
			fields=["name", "nozzle_no", "pump_number", "fuel_type", "opening_reading", "dated"],
			order_by="nozzle_no",
		)

	return {"employee": employee, "shift": shift, "open_readings": open_readings}


@frappe.whitelist()
def open_pump_reading(shift, nozzle_no, opening_reading, unit_price=None):
	"""Start a shift reading: create a draft Pump Reading with only the opening meter value."""
	frappe.has_permission("Pump Reading", "create", throw=True)
	nozzle_no = cint(nozzle_no)

	shift_doc = frappe.get_doc("Shift Assignment", shift)
	attendant = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

	doc = frappe.get_doc(
		{
			"doctype": "Pump Reading",
			"dated": today(),
			"shift": shift,
			"nozzle_no": nozzle_no,
			"opening_reading": flt(opening_reading),
			"attendant": attendant,
		}
	)
	if unit_price:
		doc.unit_price = flt(unit_price)
	doc.insert()

	matched_row = next(
		(row for row in shift_doc.assigned_pumps if cint(row.nozzle_no) == nozzle_no), None
	)
	if matched_row:
		matched_row.status = "Opened"
	else:
		shift_doc.append(
			"assigned_pumps",
			{
				"pump_number": doc.pump_number,
				"nozzle_no": nozzle_no,
				"fuel_type": doc.fuel_type,
				"status": "Opened",
			},
		)
	shift_doc.save(ignore_permissions=True)

	return doc.as_dict()


@frappe.whitelist()
def close_pump_reading(name, closing_reading, unit_price=None):
	"""Complete a shift reading: set the closing meter value and submit it."""
	doc = frappe.get_doc("Pump Reading", name)
	frappe.has_permission("Pump Reading", "submit", doc=doc, throw=True)

	doc.closing_reading = flt(closing_reading)
	if unit_price:
		doc.unit_price = flt(unit_price)
	doc.save()
	doc.submit()
	return doc.as_dict()


@frappe.whitelist()
def submit_fuel_purchase(name):
	"""Submit a draft Fuel Purchase — triggers the automatic Purchase Receipt bridge."""
	doc = frappe.get_doc("Fuel Purchase", name)
	frappe.has_permission("Fuel Purchase", "submit", doc=doc, throw=True)
	doc.submit()
	return {
		"name": doc.name,
		"docstatus": doc.docstatus,
		"purchase_receipt": doc.purchase_receipt,
	}
