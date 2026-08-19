import frappe
from frappe.utils import flt


@frappe.whitelist()
def replenish_petty_cash_account(account, amount):
	"""Top up a Petty Cash Account's balance. Wraps PettyCashAccount.replenish()."""
	frappe.has_permission("Petty Cash Account", "write", throw=True)
	amount = flt(amount)
	if amount <= 0:
		frappe.throw(frappe._("Replenishment amount must be greater than zero"))

	doc = frappe.get_doc("Petty Cash Account", account)
	doc.replenish(amount)
	return {"name": doc.name, "balance": doc.balance, "last_replenished": doc.last_replenished}
