import frappe
from frappe.model.document import Document
from frappe.utils import flt


class DebtPayment(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(frappe._("Amount must be greater than zero"))

		debt = frappe.get_doc("Customer Debt", self.customer_debt)
		if debt.docstatus != 1:
			frappe.throw(frappe._("Customer Debt must be submitted before recording a payment"))
		if flt(self.amount) > flt(debt.balance):
			frappe.throw(
				frappe._("Amount ({0}) exceeds outstanding balance ({1})").format(
					frappe.utils.fmt_money(self.amount),
					frappe.utils.fmt_money(debt.balance),
				)
			)

	def on_submit(self):
		frappe.get_doc("Customer Debt", self.customer_debt).update_balance()

	def on_cancel(self):
		frappe.get_doc("Customer Debt", self.customer_debt).update_balance()
