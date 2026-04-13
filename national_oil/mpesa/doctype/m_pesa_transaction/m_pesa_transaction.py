import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MPesaTransaction(Document):
	def on_update(self):
		if self.status == "Confirmed" and self.customer_debt and flt(self.amount) > 0:
			self._apply_to_debt()

	def _apply_to_debt(self):
		"""Create a Debt Payment when the transaction is confirmed."""
		already_applied = frappe.db.exists(
			"Debt Payment",
			{"reference": self.mpesa_receipt_number, "docstatus": 1},
		)
		if already_applied:
			return

		debt = frappe.get_doc("Customer Debt", self.customer_debt)
		if debt.docstatus != 1 or flt(debt.balance) <= 0:
			return

		payment = frappe.get_doc({
			"doctype": "Debt Payment",
			"customer_debt": self.customer_debt,
			"dated": self.dated or frappe.utils.today(),
			"amount": min(flt(self.amount), flt(debt.balance)),
			"payment_method": "M-Pesa",
			"reference": self.mpesa_receipt_number,
		})
		payment.insert(ignore_permissions=True)
		payment.submit()
