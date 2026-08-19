import frappe


def execute():
	for doctype in ("Attendance Record", "Leave Request", "NO Employee"):
		table_exists = frappe.db.table_exists(doctype)
		doctype_exists = frappe.db.exists("DocType", doctype)

		if not table_exists and not doctype_exists:
			continue
		if table_exists and frappe.db.count(doctype) > 0:
			frappe.log_error(
				title="national_oil: skipped retiring non-empty doctype",
				message=f"{doctype} still has records; delete manually after reviewing data.",
			)
			continue

		if doctype_exists:
			frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True)
		if frappe.db.table_exists(doctype):
			frappe.db.sql_ddl(f"DROP TABLE IF EXISTS `tab{doctype}`")
	frappe.db.commit()
