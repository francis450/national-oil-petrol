import frappe


ALLOWED_WORKFORCE_DOCTYPES = {
	"Employee": {
		"label_field_candidates": ["employee_name", "name"],
		"fields": ["name", "employee_name", "department", "designation", "company", "status"],
		"search_fields": ["name", "employee_name", "department", "designation", "company"],
	},
	"Driver": {
		"label_field_candidates": ["driver_name", "full_name", "name"],
		"fields": [
			"name",
			"driver_name",
			"full_name",
			"employee",
			"transporter",
			"supplier",
			"phone",
			"cell_number",
			"license_number",
			"status",
		],
		"search_fields": ["name", "driver_name", "full_name", "phone", "cell_number", "license_number"],
	},
	"Attendance": {
		"label_field_candidates": ["employee_name", "employee", "name"],
		"fields": ["name", "employee", "employee_name", "attendance_date", "department", "status", "company"],
		"search_fields": ["name", "employee", "employee_name", "department", "status"],
	},
	"Leave Application": {
		"label_field_candidates": ["employee_name", "employee", "name"],
		"fields": [
			"name",
			"employee",
			"employee_name",
			"department",
			"leave_type",
			"from_date",
			"to_date",
			"status",
		],
		"search_fields": ["name", "employee", "employee_name", "department", "leave_type", "status"],
	},
	"Shift Type": {
		"label_field_candidates": ["name"],
		"fields": ["name", "start_time", "end_time", "enable_auto_attendance", "disabled"],
		"search_fields": ["name"],
	},
	"Shift Assignment": {
		"label_field_candidates": ["employee_name", "employee", "name"],
		"fields": ["name", "employee", "employee_name", "shift_type", "start_date", "end_date", "status"],
		"search_fields": ["name", "employee", "employee_name", "shift_type", "status"],
	},
}


def _get_config(doctype: str) -> dict:
	base_config = ALLOWED_WORKFORCE_DOCTYPES.get(doctype)
	if not base_config:
		frappe.throw(frappe._("DocType {0} is not allowed for workforce lookup").format(doctype))
	if not frappe.db.exists("DocType", doctype):
		frappe.throw(frappe._("DocType {0} is not installed on this site").format(doctype))
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(frappe._("Not permitted to read {0}").format(doctype), frappe.PermissionError)

	meta = frappe.get_meta(doctype)
	available_fields = {"name"} | {field.fieldname for field in meta.fields}
	label_field = next(
		(fieldname for fieldname in base_config["label_field_candidates"] if fieldname in available_fields),
		"name",
	)

	return {
		"label_field": label_field,
		"fields": [fieldname for fieldname in base_config["fields"] if fieldname in available_fields],
		"search_fields": [
			fieldname for fieldname in base_config["search_fields"] if fieldname in available_fields
		],
	}


def _build_or_filters(search_fields: list[str], txt: str) -> list[list[str]]:
	if not txt:
		return []
	return [[field, "like", f"%{txt}%"] for field in search_fields]


@frappe.whitelist()
def list_workforce_records(
	doctype,
	txt=None,
	employee=None,
	department=None,
	status=None,
	date_from=None,
	date_to=None,
	limit_page_length=20,
):
	"""Return standardized workforce/logistics records from ERPNext and HRMS."""
	doctype = (doctype or "").strip()
	txt = (txt or "").strip()
	limit_page_length = min(max(int(limit_page_length or 20), 1), 100)

	config = _get_config(doctype)
	fields = list(dict.fromkeys(config["fields"] + [config["label_field"]]))
	filters = {}
	if employee:
		filters["employee"] = employee
	if department:
		filters["department"] = department
	if status:
		filters["status"] = status
	date_field = None
	if doctype == "Attendance":
		date_field = "attendance_date"
	elif doctype == "Leave Application":
		date_field = "from_date"

	if date_field:
		if date_from and date_to:
			filters[date_field] = ["between", [date_from, date_to]]
		elif date_from:
			filters[date_field] = [">=", date_from]
		elif date_to:
			filters[date_field] = ["<=", date_to]

	records = frappe.get_all(
		doctype,
		fields=fields,
		filters=filters,
		or_filters=_build_or_filters(config["search_fields"], txt),
		limit_page_length=limit_page_length,
		order_by="modified desc",
	)

	for record in records:
		record["label"] = record.get(config["label_field"]) or record.get("name")
		record["doctype"] = doctype

	return {
		"doctype": doctype,
		"count": len(records),
		"records": records,
	}


@frappe.whitelist()
def get_workforce_lookup_bundle():
	"""Return installed canonical workforce/logistics doctypes for the frontend."""
	bundle = []
	for doctype, config in ALLOWED_WORKFORCE_DOCTYPES.items():
		if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"):
			resolved = _get_config(doctype)
			bundle.append(
				{
					"doctype": doctype,
					"label_field": resolved["label_field"],
					"fields": resolved["fields"],
				}
			)
	return bundle
