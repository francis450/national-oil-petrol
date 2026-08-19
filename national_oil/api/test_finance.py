import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.finance import replenish_petty_cash_account


class TestFinanceApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_replenish_updates_balance_via_api(self):
		account = frappe.get_doc(
			{
				"doctype": "Petty Cash Account",
				"account_name": "NO Test Petty Cash Account API",
			}
		).insert(ignore_permissions=True)

		result = replenish_petty_cash_account(account.name, 300)

		self.assertEqual(result["balance"], 300)
		self.assertTrue(result["last_replenished"])

	def test_rejects_non_positive_amount(self):
		account = frappe.get_doc(
			{
				"doctype": "Petty Cash Account",
				"account_name": "NO Test Petty Cash Account API Zero",
			}
		).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			replenish_petty_cash_account(account.name, 0)
