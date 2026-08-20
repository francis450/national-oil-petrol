import frappe


ALLOWED_MASTER_DOCTYPES = {
	"Department": {
		"label_field": "department_name",
		"search_fields": ["name", "department_name"],
		"default_fields": ["name", "department_name"],
	},
	"Customer": {
		"label_field": "customer_name",
		"search_fields": ["name", "customer_name", "customer_group", "mobile_no"],
		"default_fields": ["name", "customer_name", "customer_group", "mobile_no", "territory"],
	},
	"Supplier": {
		"label_field": "supplier_name",
		"search_fields": ["name", "supplier_name", "supplier_group", "mobile_no"],
		"default_fields": ["name", "supplier_name", "supplier_group", "mobile_no", "supplier_type"],
	},
	"Driver": {
		"label_field": "full_name",
		"search_fields": ["name", "full_name", "license_number", "cell_number"],
		"default_fields": ["name", "full_name", "cell_number", "license_number", "status"],
	},
	"Employee": {
		"label_field": "employee_name",
		"search_fields": ["name", "employee_name", "department", "designation", "company"],
		"default_fields": ["name", "employee_name", "department", "designation", "company", "status"],
	},
	"Item": {
		"label_field": "item_name",
		"search_fields": ["name", "item_name", "item_group", "stock_uom"],
		"default_fields": ["name", "item_name", "item_group", "stock_uom", "is_stock_item", "disabled"],
	},
	"Warehouse": {
		"label_field": "warehouse_name",
		"search_fields": ["name", "warehouse_name", "company"],
		"default_fields": ["name", "warehouse_name", "company", "is_group", "disabled"],
	},
	"Fuel Type": {
		"label_field": "fuel_type_name",
		"search_fields": ["name", "fuel_type_name"],
		"default_fields": ["name", "fuel_type_name", "item", "unit_of_measure"],
	},
}


def _get_master_config(doctype: str) -> dict:
	config = ALLOWED_MASTER_DOCTYPES.get(doctype)
	if not config:
		frappe.throw(frappe._("DocType {0} is not allowed for master lookup").format(doctype))
	if not frappe.db.exists("DocType", doctype):
		frappe.throw(frappe._("DocType {0} is not installed on this site").format(doctype))
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(frappe._("Not permitted to read {0}").format(doctype), frappe.PermissionError)
	return config


def _build_or_filters(search_fields: list[str], txt: str) -> list[list[str]]:
	if not txt:
		return []
	return [[field, "like", f"%{txt}%"] for field in search_fields]


@frappe.whitelist()
def list_master_records(doctype, txt=None, limit_page_length=20, company=None):
	"""Return standardized master records from ERPNext/HRMS canonical doctypes."""
	doctype = (doctype or "").strip()
	txt = (txt or "").strip()
	limit_page_length = min(max(int(limit_page_length or 20), 1), 100)

	config = _get_master_config(doctype)
	fields = list(dict.fromkeys(config["default_fields"] + [config["label_field"]]))

	filters = {}
	if company and "company" in config["default_fields"]:
		filters["company"] = company

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
def get_master_lookup_bundle():
	"""Return lookup metadata for the canonical master doctypes used by the frontend."""
	bundle = []
	for doctype, config in ALLOWED_MASTER_DOCTYPES.items():
		if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"):
			bundle.append(
				{
					"doctype": doctype,
					"label_field": config["label_field"],
					"fields": config["default_fields"],
				}
			)
	return bundle
