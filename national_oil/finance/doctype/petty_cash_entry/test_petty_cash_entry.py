import frappe
from frappe.tests.utils import FrappeTestCase


class TestPettyCashEntry(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_account_replenish_updates_balance(self):
		account = frappe.get_doc(
			{
				"doctype": "Petty Cash Account",
				"account_name": "NO Test Petty Cash Account Replenish",
			}
		).insert(ignore_permissions=True)

		account.replenish(250)
		account.reload()

		self.assertEqual(account.balance, 250)
		self.assertTrue(account.last_replenished)

	def test_submit_and_cancel_adjust_account_balance(self):
		account = frappe.get_doc(
			{
				"doctype": "Petty Cash Account",
				"account_name": "NO Test Petty Cash Account Entry",
			}
		).insert(ignore_permissions=True)
		account.replenish(500)

		entry = frappe.get_doc(
			{
				"doctype": "Petty Cash Entry",
				"dated": "2026-04-23",
				"description": "Office supplies",
				"account": account.name,
				"amount": 200,
				"payment_method": "Cash",
			}
		).insert(ignore_permissions=True)

		entry.submit()
		account.reload()
		self.assertEqual(account.balance, 300)

		entry.cancel()
		account.reload()
		self.assertEqual(account.balance, 500)
