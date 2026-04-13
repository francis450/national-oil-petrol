import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SalesEntry(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(frappe._("Amount must be greater than zero"))
		if self.payment_method == "Credit" and not self.customer:
			frappe.throw(frappe._("Customer is required for credit sales"))
