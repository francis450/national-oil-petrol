import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PettyCashEntry(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(frappe._("Amount must be greater than zero"))

		account_balance = flt(
			frappe.db.get_value("Petty Cash Account", self.account, "balance")
		)
		if flt(self.amount) > account_balance:
			frappe.msgprint(
				frappe._("Warning: Amount exceeds current account balance of {0}").format(
					frappe.utils.fmt_money(account_balance)
				),
				alert=True,
			)

	def on_submit(self):
		account = frappe.get_doc("Petty Cash Account", self.account)
		account.balance = flt(account.balance) - flt(self.amount)
		account.save(ignore_permissions=True)

	def on_cancel(self):
		account = frappe.get_doc("Petty Cash Account", self.account)
		account.balance = flt(account.balance) + flt(self.amount)
		account.save(ignore_permissions=True)
