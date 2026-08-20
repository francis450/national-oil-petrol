import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint


class InventoryReceipt(Document):
	def validate(self):
		if cint(self.units) <= 0:
			frappe.throw(frappe._("Units Received must be greater than zero"))
		if flt(self.unit_cost) <= 0:
			frappe.throw(frappe._("Unit Cost must be greater than zero"))

		self.total_cost = flt(self.unit_cost) * cint(self.units)

		if flt(self.amount_paid) > flt(self.total_cost):
			frappe.throw(frappe._("Amount Paid cannot exceed Total Cost"))

		self.balance = self.total_cost - flt(self.amount_paid)

		if cint(self.subunits_per_unit) > 0:
			self.subunit_cost = flt(self.unit_cost) / cint(self.subunits_per_unit)

	def on_submit(self):
		self._update_product_stock(1)
		self._update_product_prices()
		if flt(self.balance) > 0:
			self._create_supplier_credit()

	def on_cancel(self):
		self._update_product_stock(-1)
		self._cancel_supplier_credit()

	def _update_product_stock(self, multiplier):
		if not self.product:
			return
		current_qty = flt(frappe.db.get_value("Product", self.product, "quantity"))
		total_units = cint(self.units) * (cint(self.subunits_per_unit) or 1)
		frappe.db.set_value("Product", self.product, "quantity", current_qty + total_units * multiplier)

	def _update_product_prices(self):
		if not self.product:
			return
		updates = {"buying_price": self.unit_cost}
		if flt(self.retail_price) > 0:
			updates["selling_price"] = self.retail_price
		if flt(self.wholesale_price) > 0:
			updates["selling_price_wholesale"] = self.wholesale_price
		frappe.db.set_value("Product", self.product, updates)

	def _create_supplier_credit(self):
		credit = frappe.get_doc({
			"doctype": "Supplier Credit",
			"supplier": self.supplier,
			"source_document_type": "Inventory Receipt",
			"source_document": self.name,
			"dated": self.dated,
			"total_amount": self.total_cost,
			"amount_paid": self.amount_paid,
			"balance": self.balance,
		})
		credit.insert(ignore_permissions=True)
		credit.submit()

	def _cancel_supplier_credit(self):
		credit = frappe.db.get_value(
			"Supplier Credit", {"source_document": self.name, "docstatus": 1}, "name"
		)
		if credit:
			frappe.get_doc("Supplier Credit", credit).cancel()
