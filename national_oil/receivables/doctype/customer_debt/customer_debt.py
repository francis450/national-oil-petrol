import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CustomerDebt(Document):
	def validate(self):
		if flt(self.payable_amount) <= 0:
			frappe.throw(frappe._("Payable Amount must be greater than zero"))

	def before_submit(self):
		self.amount_paid = 0
		self.balance = flt(self.payable_amount)
		self.status = "Open"

	def update_balance(self):
		"""Recalculate paid amount and status from submitted Debt Payments."""
		paid = frappe.db.get_value(
			"Debt Payment",
			{"customer_debt": self.name, "docstatus": 1},
			"sum(amount)",
		)
		self.amount_paid = flt(paid)
		self.balance = flt(self.payable_amount) - self.amount_paid

		if self.balance <= 0:
			self.status = "Settled"
		elif self.amount_paid > 0:
			self.status = "Partially Paid"
		else:
			self.status = "Open"

		self.db_update()
