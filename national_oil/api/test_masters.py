import frappe
from frappe.tests.utils import FrappeTestCase

from national_oil.api.masters import get_master_lookup_bundle, list_master_records


class TestMastersApi(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_disallows_unknown_doctype(self):
		with self.assertRaises(frappe.ValidationError):
			list_master_records("Brand")

	def test_lists_department_records_from_erpnext_master(self):
		department_name = "NO Test Department API"
		if not frappe.db.exists("Department", {"department_name": department_name}):
			frappe.get_doc(
				{
					"doctype": "Department",
					"department_name": department_name,
				}
			).insert(ignore_permissions=True)

		result = list_master_records("Department", txt="NO Test Department", limit_page_length=10)

		self.assertEqual(result["doctype"], "Department")
		self.assertGreaterEqual(result["count"], 1)
		self.assertTrue(any(row["department_name"] == department_name for row in result["records"]))

	def test_returns_allowed_master_bundle(self):
		result = get_master_lookup_bundle()
		doctypes = {row["doctype"] for row in result}

		self.assertIn("Department", doctypes)
		self.assertIn("Customer", doctypes)
		self.assertIn("Supplier", doctypes)
