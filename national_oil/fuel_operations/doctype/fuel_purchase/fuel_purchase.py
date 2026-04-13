import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class FuelPurchase(Document):
	def validate(self):
		if flt(self.actual_quantity) <= 0:
			frappe.throw(frappe._("Actual Quantity must be greater than zero"))
		if flt(self.unit_cost) <= 0:
			frappe.throw(frappe._("Unit Cost must be greater than zero"))
		if flt(self.amount_paid) > flt(self.total_cost):
			frappe.throw(frappe._("Amount Paid cannot exceed Total Cost"))
		if self.dated > today():
			frappe.throw(frappe._("Delivery Date cannot be in the future"))

		self.total_cost = flt(self.actual_quantity) * flt(self.unit_cost)
		self.balance = flt(self.total_cost) - flt(self.amount_paid)

	def on_submit(self):
		self._update_product_stock(1)
		if flt(self.balance) > 0:
			self._create_supplier_credit()

	def on_cancel(self):
		self._update_product_stock(-1)
		self._cancel_supplier_credit()

	def _update_product_stock(self, multiplier):
		"""Add or subtract quantity from the matching fuel Product record."""
		product = frappe.db.get_value(
			"Product", {"fuel_type": self.fuel_type, "is_fuel": 1}, "name"
		)
		if not product:
			frappe.msgprint(
				frappe._("No fuel Product found for Fuel Type {0}. Stock not updated.").format(
					self.fuel_type
				),
				alert=True,
			)
			return
		current_qty = flt(frappe.db.get_value("Product", product, "quantity"))
		new_qty = current_qty + (flt(self.actual_quantity) * multiplier)
		frappe.db.set_value("Product", product, "quantity", new_qty)

	def _create_supplier_credit(self):
		credit = frappe.get_doc(
			{
				"doctype": "Supplier Credit",
				"supplier": self.supplier,
				"source_document_type": "Fuel Purchase",
				"source_document": self.name,
				"dated": self.dated,
				"total_amount": self.total_cost,
				"amount_paid": self.amount_paid,
				"balance": self.balance,
			}
		)
		credit.insert(ignore_permissions=True)
		credit.submit()

	def _cancel_supplier_credit(self):
		credit = frappe.db.get_value(
			"Supplier Credit", {"source_document": self.name, "docstatus": 1}, "name"
		)
		if credit:
			frappe.get_doc("Supplier Credit", credit).cancel()
