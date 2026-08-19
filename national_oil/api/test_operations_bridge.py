import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.operations_bridge import (
	create_payment_entry_for_reference,
	create_erpnext_target_from_operational,
	get_operational_mapping_bundle,
	preview_erpnext_mapping,
)


class TestOperationsBridge(FrappeTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def _as_pump_attendant(self):
		user_email = "no-test-pump-attendant@example.com"
		if not frappe.db.exists("User", user_email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user_email,
					"first_name": "NO Test Pump Attendant",
					"send_welcome_email": 0,
					"roles": [{"role": "Pump Attendant"}],
				}
			).insert(ignore_permissions=True)
		frappe.set_user(user_email)

	def test_non_admin_cannot_create_erpnext_target_directly(self):
		self._as_pump_attendant()
		with self.assertRaises(frappe.PermissionError):
			create_erpnext_target_from_operational(
				"Fuel Purchase",
				"Purchase Receipt",
				doc={
					"doctype": "Fuel Purchase",
					"code": "FP-PERM-TEST-001",
					"dated": "2026-04-23",
					"supplier": "Some Supplier",
					"actual_quantity": 100,
					"unit_cost": 100,
					"total_cost": 10000,
				},
			)

	def test_non_admin_cannot_create_payment_entry_directly(self):
		self._as_pump_attendant()
		with self.assertRaises(frappe.PermissionError):
			create_payment_entry_for_reference("Purchase Invoice", "PI-DOES-NOT-EXIST")

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

	def test_creates_sales_invoice_draft_from_sales_entry(self):
		customer_name = "NO Test Customer Bridge"
		item_code = "NO-BRIDGE-SALES-ITEM"
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
		customer_group = frappe.db.get_value("Customer Group", {}, "name")
		territory = frappe.db.get_value("Territory", {}, "name")
		item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
		stock_uom = frappe.db.get_value("UOM", {}, "name")

		if not frappe.db.exists("Customer", customer_name):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_group": customer_group,
					"territory": territory,
				}
			).insert(ignore_permissions=True)

		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": "NO Bridge Sales Item",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 0,
					"is_sales_item": 1,
				}
			).insert(ignore_permissions=True)

		result = create_erpnext_target_from_operational(
			"Sales Entry",
			"Sales Invoice",
			doc={
				"doctype": "Sales Entry",
				"dated": "2026-04-23",
				"department": "Forecourt",
				"sale_type": "Other",
				"amount": 3500,
				"payment_method": "Cash",
				"customer": customer_name,
				"items": [
					{
						"doctype": "Sales Item",
						"product": item_code,
						"quantity": 1,
						"unit_price": 3500,
						"total_amount": 3500,
					}
				],
			},
			company=company,
		)

		self.assertEqual(result["target_doctype"], "Sales Invoice")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Sales Invoice", result["name"]))

	def test_creates_purchase_invoice_draft_from_fuel_purchase(self):
		supplier_name = "NO Test Supplier Bridge PI"
		item_code = "NO-BRIDGE-FUEL-ITEM-PI"
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
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
					"item_name": "NO Bridge Fuel Item PI",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 1,
					"is_purchase_item": 1,
				}
			).insert(ignore_permissions=True)

		result = create_erpnext_target_from_operational(
			"Fuel Purchase",
			"Purchase Invoice",
			doc={
				"doctype": "Fuel Purchase",
				"code": "FP-CREATE-PI-001",
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
		)

		self.assertEqual(result["target_doctype"], "Purchase Invoice")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Purchase Invoice", result["name"]))

	def test_creates_purchase_receipt_draft_from_inventory_receipt(self):
		supplier_name = "NO Test Supplier Bridge IR"
		item_code = "NO-BRIDGE-INV-ITEM-PR"
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
					"item_name": "NO Bridge Inventory Item PR",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 1,
					"is_purchase_item": 1,
				}
			).insert(ignore_permissions=True)

		result = create_erpnext_target_from_operational(
			"Inventory Receipt",
			"Purchase Receipt",
			doc={
				"doctype": "Inventory Receipt",
				"code": "IR-CREATE-PR-001",
				"dated": "2026-04-23",
				"supplier": supplier_name,
				"unit_of_measure": stock_uom,
				"units": 12,
				"subunits_per_unit": 1,
				"unit_cost": 75,
				"total_cost": 900,
				"amount_paid": 0,
			},
			item_code=item_code,
			company=company,
			warehouse=warehouse,
		)

		self.assertEqual(result["target_doctype"], "Purchase Receipt")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Purchase Receipt", result["name"]))

	def test_creates_purchase_invoice_draft_from_inventory_receipt(self):
		supplier_name = "NO Test Supplier Bridge IPI"
		item_code = "NO-BRIDGE-INV-ITEM-PI"
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
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
					"item_name": "NO Bridge Inventory Item PI",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 1,
					"is_purchase_item": 1,
				}
			).insert(ignore_permissions=True)

		result = create_erpnext_target_from_operational(
			"Inventory Receipt",
			"Purchase Invoice",
			doc={
				"doctype": "Inventory Receipt",
				"code": "IR-CREATE-PI-001",
				"dated": "2026-04-23",
				"supplier": supplier_name,
				"unit_of_measure": stock_uom,
				"units": 8,
				"subunits_per_unit": 1,
				"unit_cost": 50,
				"total_cost": 400,
				"amount_paid": 0,
			},
			item_code=item_code,
			company=company,
		)

		self.assertEqual(result["target_doctype"], "Purchase Invoice")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Purchase Invoice", result["name"]))

	def test_creates_payment_entry_draft_from_purchase_invoice(self):
		supplier_name = "NO Test Supplier Bridge PE"
		item_code = "NO-BRIDGE-FUEL-ITEM-PE"
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
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
					"item_name": "NO Bridge Fuel Item PE",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 1,
					"is_purchase_item": 1,
				}
			).insert(ignore_permissions=True)

		purchase_invoice = create_erpnext_target_from_operational(
			"Fuel Purchase",
			"Purchase Invoice",
			doc={
				"doctype": "Fuel Purchase",
				"code": "FP-CREATE-PE-001",
				"dated": "2026-04-23",
				"supplier": supplier_name,
				"fuel_type": "Petrol",
				"unit_of_measure": stock_uom,
				"actual_quantity": 100,
				"unit_cost": 125,
				"total_cost": 12500,
				"amount_paid": 0,
				"payment_method": "Cash",
			},
			item_code=item_code,
			company=company,
			submit=1,
		)

		result = create_payment_entry_for_reference(
			"Purchase Invoice",
			purchase_invoice["name"],
			payment_method="Cash",
			posting_date="2026-04-23",
		)

		self.assertEqual(result["target_doctype"], "Payment Entry")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Payment Entry", result["name"]))

	def test_creates_payment_entry_draft_from_sales_invoice(self):
		customer_name = "NO Test Customer Bridge PE"
		item_code = "NO-BRIDGE-SALES-ITEM-PE"
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
		customer_group = frappe.db.get_value("Customer Group", {}, "name")
		territory = frappe.db.get_value("Territory", {}, "name")
		item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
		stock_uom = frappe.db.get_value("UOM", {}, "name")

		if not frappe.db.exists("Customer", customer_name):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_group": customer_group,
					"territory": territory,
				}
			).insert(ignore_permissions=True)

		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": "NO Bridge Sales Item PE",
					"item_group": item_group,
					"stock_uom": stock_uom,
					"is_stock_item": 0,
					"is_sales_item": 1,
				}
			).insert(ignore_permissions=True)

		sales_invoice = create_erpnext_target_from_operational(
			"Sales Entry",
			"Sales Invoice",
			doc={
				"doctype": "Sales Entry",
				"dated": "2026-04-23",
				"department": "Forecourt",
				"sale_type": "Other",
				"amount": 3500,
				"payment_method": "Credit",
				"customer": customer_name,
				"items": [
					{
						"doctype": "Sales Item",
						"product": item_code,
						"quantity": 1,
						"unit_price": 3500,
						"total_amount": 3500,
					}
				],
			},
			company=company,
			submit=1,
		)

		result = create_payment_entry_for_reference(
			"Sales Invoice",
			sales_invoice["name"],
			payment_method="Cash",
			posting_date="2026-04-23",
		)

		self.assertEqual(result["target_doctype"], "Payment Entry")
		self.assertEqual(result["docstatus"], 0)
		self.assertTrue(frappe.db.exists("Payment Entry", result["name"]))
