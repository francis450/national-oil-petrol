import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.fuel import (
	close_pump_reading,
	get_current_prices,
	get_fuel_stock,
	get_my_shift_context,
	get_recent_pump_readings,
	open_pump_reading,
)


class TestFuelApi(FrappeTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def _ensure_fuel_type(self, name, item=None):
		if frappe.db.exists("Fuel Type", name):
			doc = frappe.get_doc("Fuel Type", name)
			if item and doc.item != item:
				doc.item = item
				doc.save(ignore_permissions=True)
			return name

		frappe.get_doc(
			{
				"doctype": "Fuel Type",
				"fuel_type_name": name,
				"unit_of_measure": "Litres",
				"item": item,
			}
		).insert(ignore_permissions=True)
		return name

	def test_returns_latest_price_per_fuel_type(self):
		fuel_type = self._ensure_fuel_type("Test Petrol")

		frappe.get_doc(
			{
				"doctype": "Fuel Price",
				"fuel_type": fuel_type,
				"effective_date": "2026-04-20",
				"buying_price": 100,
				"selling_price_retail": 120,
				"selling_price_wholesale": 115,
			}
		).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "Fuel Price",
				"fuel_type": fuel_type,
				"effective_date": "2026-04-23",
				"buying_price": 105,
				"selling_price_retail": 125,
				"selling_price_wholesale": 118,
			}
		).insert(ignore_permissions=True)

		rows = get_current_prices()
		latest = next(row for row in rows if row["fuel_type"] == fuel_type)

		self.assertEqual(str(latest["effective_date"]), "2026-04-23")
		self.assertEqual(latest["selling_price_retail"], 125)

	def test_returns_fuel_stock_rows(self):
		fuel_type = self._ensure_fuel_type("Test Diesel")

		if not frappe.db.exists("Product", "Test Diesel Product"):
			frappe.get_doc(
				{
					"doctype": "Product",
					"product_name": "Test Diesel Product",
					"is_fuel": 1,
					"fuel_type": fuel_type,
					"unit_of_measure": "Litres",
				}
			).insert(ignore_permissions=True)

		rows = get_fuel_stock()
		self.assertTrue(any(row["product_name"] == "Test Diesel Product" for row in rows))

	def test_returns_recent_pump_reading_summary(self):
		self._ensure_fuel_type("Test Kerosene", item="PARAFFIN")

		employee = frappe.db.sql(
			"""
			SELECT e.name FROM `tabEmployee` e
			WHERE e.name NOT IN (
				SELECT DISTINCT sa.employee FROM `tabShift Assignment` sa WHERE sa.docstatus < 2
			)
			LIMIT 1
			"""
		)
		employee = employee[0][0] if employee else frappe.db.get_value("Employee", {}, "name")
		shift_type = frappe.db.get_value("Shift Type", {}, "name")
		company = frappe.db.get_value("Company", {}, "name")
		shift = frappe.get_doc(
			{
				"doctype": "Shift Assignment",
				"employee": employee,
				"shift_type": shift_type,
				"company": company,
				"start_date": frappe.utils.today(),
				"end_date": frappe.utils.today(),
			}
		).insert(ignore_permissions=True).name

		frappe.get_doc(
			{
				"doctype": "Pump Reading",
				"dated": frappe.utils.today(),
				"shift": shift,
				"nozzle_no": 13,
				"opening_reading": 100,
				"closing_reading": 145,
			}
		).insert(ignore_permissions=True)

		summary = get_recent_pump_readings(limit_page_length=10)

		self.assertEqual(summary["count"], 1)
		self.assertEqual(summary["today"]["reading_count"], 1)
		self.assertEqual(summary["today"]["throughput"], 45)

	def test_open_then_close_pump_reading_closes_out_shift_for_attendant(self):
		self._ensure_fuel_type("Test Attendant Petrol", item="PETROL")

		employee = frappe.db.sql(
			"""
			SELECT e.name FROM `tabEmployee` e
			WHERE e.name NOT IN (
				SELECT DISTINCT sa.employee FROM `tabShift Assignment` sa WHERE sa.docstatus < 2
			)
			LIMIT 1
			"""
		)
		employee = employee[0][0] if employee else frappe.db.get_value("Employee", {}, "name")
		shift_type = frappe.db.get_value("Shift Type", {}, "name")
		company = frappe.db.get_value("Company", {}, "name")

		user_email = "no-test-attendant-shift@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "NO Test Attendant Shift",
					"send_welcome_email": 0,
					"roles": [{"role": "Pump Attendant"}],
				}
			).insert(ignore_permissions=True)
		frappe.db.set_value("Employee", employee, "user_id", user_email)

		shift = frappe.get_doc(
			{
				"doctype": "Shift Assignment",
				"employee": employee,
				"shift_type": shift_type,
				"company": company,
				"start_date": frappe.utils.today(),
				"end_date": frappe.utils.today(),
			}
		).insert(ignore_permissions=True)

		frappe.set_user(user_email)

		context = get_my_shift_context()
		self.assertEqual(context["employee"], employee)
		self.assertEqual(context["shift"]["name"], shift.name)
		self.assertEqual(context["open_readings"], [])

		opened = open_pump_reading(shift.name, nozzle_no=1, opening_reading=100)
		self.assertEqual(opened["docstatus"], 0)

		context = get_my_shift_context()
		self.assertEqual(len(context["open_readings"]), 1)

		closed = close_pump_reading(opened["name"], closing_reading=150, unit_price=10)
		self.assertEqual(closed["docstatus"], 1)
		self.assertEqual(closed["variance"], 50)

		shift.reload()
		self.assertEqual(shift.reconciliation_status, "Closed")
		self.assertEqual(shift.total_expected_sales, 500)
