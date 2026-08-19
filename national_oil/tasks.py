import frappe
from frappe.utils import today


def settle_supplier_credits():
	"""Mark Supplier Credits as Settled when balance = 0. (Payables — stays active.)"""
	frappe.db.sql("""
		UPDATE `tabSupplier Credit`
		SET status = 'Settled'
		WHERE docstatus = 1 AND balance <= 0 AND status != 'Settled'
	""")


def auto_settle_debts():
	"""
	PARKED pending a credit-sales decision (see docs/ERP_REUSE_STRATEGY.md). This used to also
	settle Supplier Credit (Payables) — that half was split out into settle_supplier_credits(),
	which stays scheduled, so parking Receivables doesn't also stop Payables automation.
	Not wired into scheduler_events; kept here for when Receivables is unparked.
	"""
	frappe.db.sql("""
		UPDATE `tabCustomer Debt`
		SET status = 'Settled'
		WHERE docstatus = 1 AND balance <= 0 AND status != 'Settled'
	""")


def refresh_sales_targets():
	"""Recalculate hit_amount and deviation for all active Department Sales Targets."""
	targets = frappe.get_all(
		"Department Sales Target",
		filters={"period_start": ("<=", today())},
		fields=["name"],
	)
	for t in targets:
		doc = frappe.get_doc("Department Sales Target", t.name)
		doc.recalculate()


def send_debt_reminders():
	"""
	PARKED pending a credit-sales decision (see docs/ERP_REUSE_STRATEGY.md).
	Not wired into scheduler_events; kept here for when Receivables is unparked.
	Email customers with open debts (stub — extend with email template).
	"""
	open_debts = frappe.get_all(
		"Customer Debt",
		filters={"status": ("in", ["Open", "Partially Paid"]), "docstatus": 1},
		fields=["name", "customer", "balance"],
	)
	for debt in open_debts:
		customer_email = frappe.db.get_value("Customer", debt.customer, "email_id")
		if customer_email:
			frappe.sendmail(
				recipients=[customer_email],
				subject="Payment Reminder — National Oil",
				message=f"Dear {debt.customer},<br><br>"
				        f"You have an outstanding balance of KSh {debt.balance:,.2f}.<br>"
				        f"Please settle at your earliest convenience.<br><br>"
				        f"Thank you.",
			)

