import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.fuel import get_current_prices, get_fuel_stock, get_recent_pump_readings


class TestFuelApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _ensure_fuel_type(self, name):
		if frappe.db.exists("Fuel Type", name):
			return name

		frappe.get_doc(
			{
				"doctype": "Fuel Type",
				"fuel_type_name": name,
				"unit_of_measure": "Litres",
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
		fuel_type = self._ensure_fuel_type("Test Kerosene")

		frappe.get_doc(
			{
				"doctype": "Pump Reading",
				"dated": "2026-04-23",
				"pump_number": "P-01",
				"fuel_type": fuel_type,
				"opening_reading": 100,
				"closing_reading": 145,
			}
		).insert(ignore_permissions=True)

		summary = get_recent_pump_readings(limit_page_length=10)

		self.assertEqual(summary["count"], 1)
		self.assertEqual(summary["today"]["reading_count"], 1)
		self.assertEqual(summary["today"]["throughput"], 45)
