import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.commerce import get_commerce_lookup_bundle, list_commerce_records


class TestCommerceApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_disallows_unknown_commerce_doctype(self):
		with self.assertRaises(frappe.ValidationError):
			list_commerce_records("Product")

	def test_lists_item_records_from_erpnext_item_master(self):
		item_code = "NO-TEST-ITEM-API"
		item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
		stock_uom = frappe.db.get_value("UOM", "Nos", "name") or frappe.db.get_value("UOM", {}, "name")

		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": "NO Test Item API",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 1,
				}
			).insert(ignore_permissions=True)

		result = list_commerce_records("Item", txt="NO Test Item", limit_page_length=10)

		self.assertEqual(result["doctype"], "Item")
		self.assertGreaterEqual(result["count"], 1)
		self.assertTrue(any(row["item_code"] == item_code for row in result["records"]))

	def test_returns_installed_commerce_bundle(self):
		result = get_commerce_lookup_bundle()
		doctypes = {row["doctype"] for row in result}

		self.assertIn("Item", doctypes)
		self.assertIn("Purchase Receipt", doctypes)
		self.assertIn("Purchase Invoice", doctypes)
		self.assertIn("Sales Invoice", doctypes)
		self.assertIn("Payment Entry", doctypes)
