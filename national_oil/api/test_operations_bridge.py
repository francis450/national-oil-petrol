import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.operations_bridge import (
	create_erpnext_target_from_operational,
	get_operational_mapping_bundle,
	preview_erpnext_mapping,
)


class TestOperationsBridge(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_returns_supported_operational_bundle(self):
		bundle = get_operational_mapping_bundle()
		self.assertIn("Fuel Purchase", bundle)
		self.assertIn("Inventory Receipt", bundle)
		self.assertIn("Sales Entry", bundle)

	def test_previews_fuel_purchase_targets(self):
		preview = preview_erpnext_mapping(
			"Fuel Purchase",
			doc={
				"doctype": "Fuel Purchase",
				"code": "FP-TEST-001",
				"dated": "2026-04-23",
				"supplier": "Test Supplier",
				"fuel_type": "Petrol",
				"unit_of_measure": "Litres",
				"actual_quantity": 1000,
				"unit_cost": 120,
				"total_cost": 120000,
				"amount_paid": 50000,
				"payment_method": "Cash",
			},
		)

		target_doctypes = [target["target_doctype"] for target in preview["targets"]]
		self.assertIn("Purchase Receipt", target_doctypes)
		self.assertIn("Purchase Invoice", target_doctypes)
		self.assertIn("Payment Entry", target_doctypes)

	def test_previews_sales_entry_targets_and_flags_missing_customer(self):
		preview = preview_erpnext_mapping(
			"Sales Entry",
			doc={
				"doctype": "Sales Entry",
				"dated": "2026-04-23",
				"department": "Forecourt",
				"sale_type": "Wet Stock",
				"amount": 25000,
				"payment_method": "Cash",
				"items": [
					{
						"doctype": "Sales Item",
						"product": "Unknown Product",
						"quantity": 10,
						"unit_price": 2500,
						"total_amount": 25000,
					}
				],
			},
		)

		sales_invoice_target = next(
			target for target in preview["targets"] if target["target_doctype"] == "Sales Invoice"
		)
		self.assertTrue(
			any("Customer is required" in message for message in sales_invoice_target["unresolved_dependencies"])
		)

	def test_creates_purchase_receipt_draft_from_fuel_purchase(self):
		supplier_name = "NO Test Supplier Bridge"
		item_code = "NO-BRIDGE-FUEL-ITEM"
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
		warehouse = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")
		supplier_group = frappe.db.get_value("Supplier Group", {}, "name")
		item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
		stock_uom = frappe.db.get_value("UOM", {}, "name")

		if not frappe.db.exists("Supplier", supplier_name):
			frappe.get_doc(
				{
					"doctype": "Supplier",
					"supplier_name": supplier_name,
					"supplier_group": supplier_group,
				}
			).insert(ignore_permissions=True)

		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": "NO Bridge Fuel Item",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 1,
					"is_purchase_item": 1,
				}
			).insert(ignore_permissions=True)

		result = create_erpnext_target_from_operational(
			"Fuel Purchase",
			"Purchase Receipt",
			doc={
				"doctype": "Fuel Purchase",
				"code": "FP-CREATE-001",
				"dated": "2026-04-23",
				"supplier": supplier_name,
				"fuel_type": "Petrol",
				"unit_of_measure": stock_uom,
				"actual_quantity": 100,
				"unit_cost": 125,
				"total_cost": 12500,
				"amount_paid": 0,
			},
			item_code=item_code,
			company=company,
			warehouse=warehouse,
		)

		self.assertEqual(result["target_doctype"], "Purchase Receipt")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Purchase Receipt", result["name"]))
