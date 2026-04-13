import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_customer_balance(customer):
	"""Total payable, paid, and outstanding for a customer."""
	result = frappe.db.sql("""
		SELECT
			SUM(payable_amount) AS total_payable,
			SUM(amount_paid)    AS total_paid,
			SUM(balance)        AS total_balance
		FROM `tabCustomer Debt`
		WHERE customer = %s AND docstatus = 1
	""", customer, as_dict=True)
	return result[0] if result else {}


@frappe.whitelist()
def record_debt_payment(customer_debt, amount, payment_method="Cash", reference=None, dated=None):
	"""Create and submit a Debt Payment in one call."""
	frappe.has_permission("Debt Payment", "create", throw=True)
	doc = frappe.get_doc({
		"doctype": "Debt Payment",
		"customer_debt": customer_debt,
		"amount": flt(amount),
		"payment_method": payment_method,
		"reference": reference,
		"dated": dated or frappe.utils.today(),
	})
	doc.insert()
	doc.submit()
	return doc.name
