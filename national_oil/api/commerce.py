import frappe


ALLOWED_COMMERCE_DOCTYPES = {
	"Item": {
		"label_field_candidates": ["item_name", "item_code", "name"],
		"fields": [
			"name",
			"item_code",
			"item_name",
			"item_group",
			"stock_uom",
			"is_stock_item",
			"is_sales_item",
			"is_purchase_item",
			"disabled",
		],
		"search_fields": ["name", "item_code", "item_name", "item_group", "stock_uom"],
	},
	"Purchase Receipt": {
		"label_field_candidates": ["supplier_name", "supplier", "name"],
		"fields": ["name", "supplier", "supplier_name", "posting_date", "company", "status", "grand_total"],
		"search_fields": ["name", "supplier", "supplier_name", "status", "company"],
	},
	"Purchase Invoice": {
		"label_field_candidates": ["supplier_name", "supplier", "name"],
		"fields": [
			"name",
			"supplier",
			"supplier_name",
			"posting_date",
			"company",
			"docstatus",
			"status",
			"grand_total",
			"outstanding_amount",
		],
		"search_fields": ["name", "supplier", "supplier_name", "bill_no", "status", "company"],
	},
	"Sales Invoice": {
		"label_field_candidates": ["customer_name", "customer", "name"],
		"fields": [
			"name",
			"customer",
			"customer_name",
			"posting_date",
			"company",
			"docstatus",
			"is_pos",
			"status",
			"grand_total",
			"outstanding_amount",
		],
		"search_fields": ["name", "customer", "customer_name", "po_no", "status", "company"],
	},
	"Payment Entry": {
		"label_field_candidates": ["party_name", "party", "name"],
		"fields": [
			"name",
			"payment_type",
			"party_type",
			"party",
			"party_name",
			"posting_date",
			"company",
			"paid_amount",
			"received_amount",
			"mode_of_payment",
			"status",
		],
		"search_fields": ["name", "party", "party_name", "payment_type", "mode_of_payment", "status"],
	},
}


def _resolve_config(doctype: str) -> dict:
	base_config = ALLOWED_COMMERCE_DOCTYPES.get(doctype)
	if not base_config:
		frappe.throw(frappe._("DocType {0} is not allowed for commerce lookup").format(doctype))
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
def list_commerce_records(
	doctype,
	txt=None,
	party=None,
	company=None,
	status=None,
	date_from=None,
	date_to=None,
	limit_page_length=20,
):
	"""Return standardized commerce and stock records from ERPNext canonical doctypes."""
	doctype = (doctype or "").strip()
	txt = (txt or "").strip()
	limit_page_length = min(max(int(limit_page_length or 20), 1), 100)

	config = _resolve_config(doctype)
	filters = {}

	if company and "company" in config["fields"]:
		filters["company"] = company
	if status and "status" in config["fields"]:
		filters["status"] = status

	if party:
		if doctype in {"Purchase Receipt", "Purchase Invoice"} and "supplier" in config["fields"]:
			filters["supplier"] = party
		elif doctype == "Sales Invoice" and "customer" in config["fields"]:
			filters["customer"] = party
		elif doctype == "Payment Entry" and "party" in config["fields"]:
			filters["party"] = party

	date_field = "posting_date" if "posting_date" in config["fields"] else None
	if date_field:
		if date_from and date_to:
			filters[date_field] = ["between", [date_from, date_to]]
		elif date_from:
			filters[date_field] = [">=", date_from]
		elif date_to:
			filters[date_field] = ["<=", date_to]

	records = frappe.get_all(
		doctype,
		fields=config["fields"],
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
def get_commerce_lookup_bundle():
	"""Return installed canonical commerce doctypes for the frontend."""
	bundle = []
	for doctype in ALLOWED_COMMERCE_DOCTYPES:
		if frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"):
			resolved = _resolve_config(doctype)
			bundle.append(
				{
					"doctype": doctype,
					"label_field": resolved["label_field"],
					"fields": resolved["fields"],
				}
			)
	return bundle
