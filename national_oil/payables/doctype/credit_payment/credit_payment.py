import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CreditPayment(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(frappe._("Amount must be greater than zero"))

		credit = frappe.get_doc("Supplier Credit", self.supplier_credit)
		if credit.docstatus != 1:
			frappe.throw(frappe._("Supplier Credit must be submitted before recording a payment"))
		if flt(self.amount) > flt(credit.balance):
			frappe.throw(
				frappe._("Amount ({0}) exceeds outstanding balance ({1})").format(
					frappe.utils.fmt_money(self.amount),
					frappe.utils.fmt_money(credit.balance),
				)
			)

	def on_submit(self):
		frappe.get_doc("Supplier Credit", self.supplier_credit).update_balance()

	def on_cancel(self):
		frappe.get_doc("Supplier Credit", self.supplier_credit).update_balance()
