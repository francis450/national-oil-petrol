import frappe
from frappe.tests.utils import FrappeTestCase


class TestFuelPurchase(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _ensure_supplier(self, name):
		if frappe.db.exists("Supplier", name):
			return name
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": name,
				"supplier_group": frappe.db.get_value("Supplier Group", {}, "name"),
			}
		).insert(ignore_permissions=True)
		return name

	def _ensure_fuel_type(self, name, item):
		if frappe.db.exists("Fuel Type", name):
			doc = frappe.get_doc("Fuel Type", name)
			if doc.item != item:
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

	def test_submit_creates_and_links_purchase_receipt(self):
		supplier = self._ensure_supplier("NO Test Fuel Purchase Supplier")
		self._ensure_fuel_type("Test Fuel Purchase Petrol", "PETROL")
		warehouse = frappe.db.get_value("Warehouse", {"name": ["like", "%Petrol Tank%"]}, "name") or frappe.db.get_value(
			"Warehouse", {"is_group": 0}, "name"
		)

		doc = frappe.get_doc(
			{
				"doctype": "Fuel Purchase",
				"code": f"FP-TEST-{frappe.generate_hash(length=6)}",
				"dated": frappe.utils.today(),
				"supplier": supplier,
				"fuel_type": "Test Fuel Purchase Petrol",
				"unit_of_measure": "Litres",
				"actual_quantity": 200,
				"unit_cost": 150,
				"payment_method": "Credit",
				"warehouse": warehouse,
			}
		)
		doc.insert(ignore_permissions=True)
		doc.submit()

		self.assertTrue(doc.purchase_receipt)
		self.assertTrue(frappe.db.exists("Purchase Receipt", doc.purchase_receipt))
		self.assertEqual(frappe.db.get_value("Purchase Receipt", doc.purchase_receipt, "docstatus"), 1)

		doc.cancel()
		self.assertEqual(frappe.db.get_value("Purchase Receipt", doc.purchase_receipt, "docstatus"), 2)
