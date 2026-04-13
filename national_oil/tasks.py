import frappe
from frappe.utils import today


def auto_settle_debts():
	"""Mark Customer Debts and Supplier Credits as Settled when balance = 0."""
	frappe.db.sql("""
		UPDATE `tabCustomer Debt`
		SET status = 'Settled'
		WHERE docstatus = 1 AND balance <= 0 AND status != 'Settled'
	""")
	frappe.db.sql("""
		UPDATE `tabSupplier Credit`
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
	"""Email customers with open debts (stub — extend with email template)."""
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


def backup_report_snapshot():
	"""Placeholder for monthly archive logic."""
	frappe.logger().info("national_oil: monthly snapshot task ran on %s", today())
