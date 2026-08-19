import frappe
from frappe.permissions import setup_custom_perms


def execute():
	if "hrms" not in frappe.get_installed_apps():
		return

	setup_custom_perms("Shift Assignment")

	for role in ("Station Manager", "HR Officer"):
		if frappe.db.exists("Custom DocPerm", {"parent": "Shift Assignment", "role": role, "permlevel": 0}):
			continue
		frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": "Shift Assignment",
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"permlevel": 0,
				"read": 1,
				"write": 1,
				"create": 1,
				"submit": 1,
				"cancel": 1,
				"amend": 1,
			}
		).insert(ignore_permissions=True)

	frappe.clear_cache(doctype="Shift Assignment")
