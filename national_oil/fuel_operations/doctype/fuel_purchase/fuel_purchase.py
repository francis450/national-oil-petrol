import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate

# Ported from nog_erpnext/forecourt/utils.py — canonical tank per fuel item.
FUEL_TANK_WAREHOUSE = {
	"PETROL": "Petrol Tank - NOG",
	"DIESEL": "Diesel Tank  - NOG",
	"PARAFFIN": "Paraffin Tank  - NOG",
}


class FuelPurchase(Document):
	def validate(self):
		if flt(self.actual_quantity) <= 0:
			frappe.throw(frappe._("Actual Quantity must be greater than zero"))
		if flt(self.unit_cost) <= 0:
			frappe.throw(frappe._("Unit Cost must be greater than zero"))
		if getdate(self.dated) > getdate():
			frappe.throw(frappe._("Delivery Date cannot be in the future"))

		self.total_cost = flt(self.actual_quantity) * flt(self.unit_cost)

		if flt(self.amount_paid) > flt(self.total_cost):
			frappe.throw(frappe._("Amount Paid cannot exceed Total Cost"))

		self.balance = flt(self.total_cost) - flt(self.amount_paid)

		if not self.warehouse and self.item_code:
			self.warehouse = self._get_existing_warehouse(FUEL_TANK_WAREHOUSE.get(self.item_code))

	def on_submit(self):
		self._update_product_stock(1)
		if flt(self.balance) > 0:
			self._create_supplier_credit()
		if not self.purchase_receipt:
			self._create_purchase_receipt()

	def on_cancel(self):
		self._update_product_stock(-1)
		self._cancel_supplier_credit()
		self._cancel_purchase_receipt()

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

	def _create_purchase_receipt(self):
		from national_oil.api.operations_bridge import create_erpnext_target_from_operational

		if not self.item_code:
			frappe.msgprint(
				frappe._(
					"No ERPNext Item is linked for Fuel Type {0}. Purchase Receipt was not created — "
					"set the Item on the Fuel Type and resubmit an amendment."
				).format(self.fuel_type),
				alert=True,
			)
			return

		result = create_erpnext_target_from_operational(
			source_doctype="Fuel Purchase",
			target_doctype="Purchase Receipt",
			docname=self.name,
			warehouse=self.warehouse,
			item_code=self.item_code,
			submit=1,
		)
		self.db_set("purchase_receipt", result.get("name"), update_modified=False)

	def _cancel_purchase_receipt(self):
		if not self.purchase_receipt or not frappe.db.exists("Purchase Receipt", self.purchase_receipt):
			return
		receipt = frappe.get_doc("Purchase Receipt", self.purchase_receipt)
		if receipt.docstatus == 1:
			receipt.flags.ignore_permissions = True
			receipt.cancel()

	@staticmethod
	def _get_existing_warehouse(warehouse):
		if not warehouse:
			return None
		if frappe.db.exists("Warehouse", warehouse):
			return warehouse
		normalized = " ".join(warehouse.split())
		for candidate in frappe.get_all("Warehouse", pluck="name"):
			if " ".join(candidate.split()) == normalized:
				return candidate
		return warehouse
