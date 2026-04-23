import frappe
from frappe.tests.utils import FrappeTestCase


class TestDepartmentSalesTarget(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _get_department(self):
		department = frappe.db.get_value("Department", {}, "name")
		if department:
			return department
		self.skipTest("Department master data is not available on this site.")

	def test_validate_requires_positive_target_amount(self):
		department = self._get_department()

		target = frappe.get_doc(
			{
				"doctype": "Department Sales Target",
				"department": department,
				"period_type": "Monthly",
				"period_start": "2026-04-01",
				"period_end": "2026-04-30",
				"target_amount": 0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			target.insert(ignore_permissions=True)

	def test_recalculate_uses_submitted_sales_entries(self):
		department = self._get_department()

		frappe.get_doc(
			{
				"doctype": "Sales Entry",
				"dated": "2026-04-10",
				"department": department,
				"sale_type": "Other",
				"amount": 1500,
				"payment_method": "Cash",
			}
		).insert(ignore_permissions=True).submit()

		frappe.get_doc(
			{
				"doctype": "Sales Entry",
				"dated": "2026-04-15",
				"department": department,
				"sale_type": "Other",
				"amount": 2500,
				"payment_method": "Cash",
			}
		).insert(ignore_permissions=True).submit()

		target = frappe.get_doc(
			{
				"doctype": "Department Sales Target",
				"department": department,
				"period_type": "Monthly",
				"period_start": "2026-04-01",
				"period_end": "2026-04-30",
				"target_amount": 3000,
			}
		).insert(ignore_permissions=True)

		target.recalculate()
		target.reload()

		self.assertEqual(target.hit_amount, 4000)
		self.assertEqual(target.deviation, 1000)
		self.assertAlmostEqual(target.variance_percent, 33.3333333333, places=2)
