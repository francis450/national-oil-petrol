import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.dashboard import get_dashboard_metrics, get_sales_trend
from national_oil.api.operations_bridge import create_erpnext_target_from_operational


class TestDashboardApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _ensure_customer(self, customer_name):
		if frappe.db.exists("Customer", customer_name):
			return customer_name

		customer_group = frappe.db.get_value("Customer Group", {}, "name")
		territory = frappe.db.get_value("Territory", {}, "name")
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_group": customer_group,
				"territory": territory,
			}
		).insert(ignore_permissions=True)
		return customer_name

	def _ensure_supplier(self, supplier_name):
		if frappe.db.exists("Supplier", supplier_name):
			return supplier_name

		supplier_group = frappe.db.get_value("Supplier Group", {}, "name")
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": supplier_name,
				"supplier_group": supplier_group,
			}
		).insert(ignore_permissions=True)
		return supplier_name

	def _ensure_item(self, item_code, *, sales_item=False, purchase_item=False):
		if frappe.db.exists("Item", item_code):
			return item_code

		item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
		stock_uom = frappe.db.get_value("UOM", {}, "name")
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_code,
				"item_group": item_group,
				"stock_uom": stock_uom,
				"is_stock_item": 0,
				"is_sales_item": 1 if sales_item else 0,
				"is_purchase_item": 1 if purchase_item else 0,
			}
		).insert(ignore_permissions=True)
		return item_code

	def test_returns_dashboard_shape_when_site_is_sparse(self):
		metrics = get_dashboard_metrics()

		for key in [
			"today_sales",
			"month_sales",
			"outstanding_receivables",
			"outstanding_payables",
			"stock_balance_qty",
			"operational_backlog",
			"sales_trend",
			"stock_levels",
			"attendance",
			"pipeline",
			"settlement",
		]:
			self.assertIn(key, metrics)

		self.assertEqual(len(metrics["sales_trend"]), 7)
		self.assertEqual(len(metrics["attendance"]), 2)
		self.assertEqual(len(metrics["pipeline"]), 3)

	def test_aggregates_posted_sales_and_payables_from_erpnext_docs(self):
		company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value(
			"Company", {}, "name"
		)
		customer_name = self._ensure_customer("NO Dashboard Customer")
		supplier_name = self._ensure_supplier("NO Dashboard Supplier")
		sales_item = self._ensure_item("NO-DASHBOARD-SALES-ITEM", sales_item=True)
		purchase_item = self._ensure_item("NO-DASHBOARD-PURCHASE-ITEM", purchase_item=True)

		create_erpnext_target_from_operational(
			"Sales Entry",
			"Sales Invoice",
			doc={
				"doctype": "Sales Entry",
				"dated": "2026-04-23",
				"department": "Forecourt",
				"sale_type": "Other",
				"amount": 4200,
				"payment_method": "Credit",
				"customer": customer_name,
				"items": [
					{
						"doctype": "Sales Item",
						"product": sales_item,
						"quantity": 1,
						"unit_price": 4200,
						"total_amount": 4200,
					}
				],
			},
			company=company,
			submit=1,
		)

		create_erpnext_target_from_operational(
			"Fuel Purchase",
			"Purchase Invoice",
			doc={
				"doctype": "Fuel Purchase",
				"code": "FP-DASHBOARD-001",
				"dated": "2026-04-23",
				"supplier": supplier_name,
				"fuel_type": "Petrol",
				"unit_of_measure": frappe.db.get_value("UOM", {}, "name"),
				"actual_quantity": 10,
				"unit_cost": 150,
				"total_cost": 1500,
				"amount_paid": 0,
			},
			item_code=purchase_item,
			company=company,
			submit=1,
		)

		metrics = get_dashboard_metrics()
		trend = get_sales_trend(7)

		self.assertGreater(metrics["today_sales"], 0)
		self.assertGreater(metrics["month_sales"], 0)
		self.assertGreater(metrics["outstanding_receivables"], 0)
		self.assertGreater(metrics["outstanding_payables"], 0)
		self.assertTrue(any(point["value"] > 0 for point in trend))
