import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.workforce import get_workforce_lookup_bundle, list_workforce_records


class TestWorkforceApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_disallows_unknown_workforce_doctype(self):
		with self.assertRaises(frappe.ValidationError):
			list_workforce_records("NO Employee")

	def test_lists_driver_records_from_erpnext_doctype(self):
		driver_name = "NO Test Driver API"
		if not (
			frappe.db.exists("Driver", {"driver_name": driver_name})
			or frappe.db.exists("Driver", {"full_name": driver_name})
		):
			frappe.get_doc(
				{
					"doctype": "Driver",
					"driver_name": driver_name,
					"status": "Active",
				}
			).insert(ignore_permissions=True)

		result = list_workforce_records("Driver", txt="NO Test Driver", limit_page_length=10)

		self.assertEqual(result["doctype"], "Driver")
		self.assertGreaterEqual(result["count"], 1)
		self.assertTrue(any(row["label"] == driver_name for row in result["records"]))

	def test_returns_installed_workforce_bundle(self):
		result = get_workforce_lookup_bundle()
		doctypes = {row["doctype"] for row in result}

		self.assertIn("Employee", doctypes)
		self.assertIn("Driver", doctypes)
		self.assertIn("Attendance", doctypes)
		self.assertIn("Leave Application", doctypes)
