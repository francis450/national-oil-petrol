import frappe
from frappe.tests.utils import FrappeTestCase


class TestSalesEntry(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create_shift_assignment(self, total_expected_sales):
		employee = frappe.db.sql(
			"""
			SELECT e.name FROM `tabEmployee` e
			WHERE e.name NOT IN (
				SELECT DISTINCT sa.employee FROM `tabShift Assignment` sa WHERE sa.docstatus < 2
			)
			LIMIT 1
			"""
		)
		employee = employee[0][0] if employee else frappe.db.get_value("Employee", {}, "name")
		shift_type = frappe.db.get_value("Shift Type", {}, "name")
		company = frappe.db.get_value("Company", {}, "name")
		doc = frappe.get_doc(
			{
				"doctype": "Shift Assignment",
				"employee": employee,
				"shift_type": shift_type,
				"company": company,
				"start_date": frappe.utils.today(),
				"end_date": frappe.utils.today(),
			}
		).insert(ignore_permissions=True)
		frappe.db.set_value("Shift Assignment", doc.name, "total_expected_sales", total_expected_sales)
		return doc.name

	def _ensure_department(self):
		name = frappe.db.get_value("Department", {}, "name")
		self.assertTrue(name, "No Department exists on this site to run this test against")
		return name

	def test_variance_is_computed_but_never_blocks_save(self):
		shift = self._create_shift_assignment(total_expected_sales=1000)
		department = self._ensure_department()

		doc = frappe.get_doc(
			{
				"doctype": "Sales Entry",
				"dated": frappe.utils.today(),
				"department": department,
				"sale_type": "Wet Stock",
				"amount": 850,
				"payment_method": "Cash",
				"shift": shift,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(doc.variance_from_pump_reading, -150)

		doc.submit()
		self.assertEqual(doc.docstatus, 1)

	def test_variance_blank_without_shift(self):
		department = self._ensure_department()

		doc = frappe.get_doc(
			{
				"doctype": "Sales Entry",
				"dated": frappe.utils.today(),
				"department": department,
				"sale_type": "Other",
				"amount": 500,
				"payment_method": "Cash",
			}
		).insert(ignore_permissions=True)

		self.assertFalse(doc.variance_from_pump_reading)
