import frappe
from frappe.utils import cint, flt
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry


OPERATIONAL_MAPPING_BUNDLE = {
	"Fuel Purchase": {
		"targets": ["Purchase Receipt", "Purchase Invoice", "Payment Entry"],
		"purpose": "Wet-stock operational delivery capture before ERPNext stock and accounting posting.",
	},
	"Inventory Receipt": {
		"targets": ["Purchase Receipt", "Purchase Invoice", "Payment Entry"],
		"purpose": "Operational receiving flow for non-fuel stock before ERPNext commercial posting.",
	},
	"Sales Entry": {
		"targets": ["Sales Invoice", "Payment Entry"],
		"purpose": "Operational sales capture before ERPNext invoicing and settlement.",
	},
}

PAYMENT_MODE_MAP = {
	"Cash": "Cash",
	"M-Pesa": "M-Pesa",
	"Cheque": "Cheque",
	"Bank Transfer": "Wire Transfer",
	"Credit": None,
}


def _coerce_source_doc(source_doctype, docname=None, doc=None):
	if source_doctype not in OPERATIONAL_MAPPING_BUNDLE:
		frappe.throw(frappe._("Unsupported source doctype {0}").format(source_doctype))

	frappe.has_permission(source_doctype, "read", throw=True)

	if doc is not None:
		doc = frappe.parse_json(doc) if isinstance(doc, str) else doc
		if isinstance(doc, dict):
			doc.setdefault("doctype", source_doctype)
			return frappe.get_doc(doc)
		return doc

	if not docname:
		frappe.throw(frappe._("Either docname or doc payload is required"))

	return frappe.get_doc(source_doctype, docname)


def _candidate_item_codes(*values):
	candidates = []
	for value in values:
		if value and value not in candidates:
			candidates.append(value)
	return candidates


def _find_item_code(*values):
	for candidate in _candidate_item_codes(*values):
		if frappe.db.exists("Item", candidate):
			return candidate
		item_by_name = frappe.db.get_value("Item", {"item_name": candidate}, "name")
		if item_by_name:
			return item_by_name
	return None


def _payment_mode(payment_method):
	return PAYMENT_MODE_MAP.get(payment_method)


def _resolve_mode_of_payment(company, payment_method=None, mode_of_payment=None):
	candidate = mode_of_payment or _payment_mode(payment_method)
	if not candidate:
		return None, None
	if not frappe.db.exists("Mode of Payment", candidate):
		return candidate, None
	account = frappe.db.get_value(
		"Mode of Payment Account", {"parent": candidate, "company": company}, "default_account"
	)
	return candidate, account


def _get_default_company():
	return (
		frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_value("Company", {}, "name")
	)


def _warehouse_belongs_to_company(warehouse, company):
	if not warehouse or not company:
		return False
	return frappe.db.get_value("Warehouse", warehouse, "company") == company


def _get_default_warehouse(company=None):
	filters = {"is_group": 0}
	if company:
		filters["company"] = company
	return frappe.db.get_value("Warehouse", filters, "name")


def _get_item_default_warehouse(item_code, company=None, warehouse=None):
	if warehouse and _warehouse_belongs_to_company(warehouse, company):
		return warehouse

	if company:
		item_default_warehouse = frappe.db.get_value(
			"Item Default",
			{"parent": item_code, "company": company},
			"default_warehouse",
		)
		if item_default_warehouse and _warehouse_belongs_to_company(item_default_warehouse, company):
			return item_default_warehouse

	return (
		frappe.db.get_value("Item Default", {"parent": item_code}, "default_warehouse")
		if not company
		else None
	) or _get_default_warehouse(company=company)


def _resolve_stock_warehouse(company, item_code=None, warehouse=None):
	if warehouse and _warehouse_belongs_to_company(warehouse, company):
		return warehouse
	if item_code:
		resolved = _get_item_default_warehouse(item_code, company=company, warehouse=warehouse)
		if resolved and _warehouse_belongs_to_company(resolved, company):
			return resolved
	return _get_default_warehouse(company=company)


def _warehouse_resolution_message(source_label, company):
	return f"No ERPNext Warehouse could be resolved for {source_label} in company {company}."


def _is_stock_item(item_code):
	return bool(frappe.db.get_value("Item", item_code, "is_stock_item")) if item_code else False


def _build_fuel_purchase_purchase_receipt_payload(doc, company=None, warehouse=None, item_code=None):
	resolved_item_code = item_code or _find_item_code(
		getattr(doc, "item_code", None),
		getattr(doc, "erpnext_item", None),
		getattr(doc, "fuel_type", None),
		getattr(doc, "brand", None),
	)
	resolved_company = company or getattr(doc, "company", None) or _get_default_company()
	resolved_warehouse = _resolve_stock_warehouse(
		resolved_company,
		item_code=resolved_item_code,
		warehouse=warehouse or getattr(doc, "warehouse", None),
	)

	unresolved = []
	if not resolved_item_code:
		unresolved.append("No canonical ERPNext Item could be resolved for this fuel purchase.")
	if not resolved_company:
		unresolved.append("No ERPNext Company could be resolved for this fuel purchase.")
	if not resolved_warehouse:
		unresolved.append(_warehouse_resolution_message("this fuel purchase", resolved_company))

	item_uom = None
	if resolved_item_code:
		item_uom = frappe.db.get_value("Item", resolved_item_code, "stock_uom")

	payload = {
		"doctype": "Purchase Receipt",
		"supplier": doc.supplier,
		"posting_date": doc.dated,
		"company": resolved_company,
		"set_warehouse": resolved_warehouse,
		"supplier_delivery_note": doc.code,
		"items": [
			{
				"item_code": resolved_item_code,
				"qty": flt(doc.actual_quantity),
				"uom": item_uom or getattr(doc, "unit_of_measure", None),
				"stock_uom": item_uom,
				"warehouse": resolved_warehouse,
				"rate": flt(doc.unit_cost),
				"amount": flt(doc.total_cost),
			}
		],
		"remarks": f"Mapped from Fuel Purchase {getattr(doc, 'name', 'unsaved')} / {doc.code}",
	}
	return payload, unresolved


def _build_fuel_purchase_purchase_invoice_payload(doc, company=None, item_code=None):
	resolved_item_code = item_code or _find_item_code(
		getattr(doc, "item_code", None),
		getattr(doc, "erpnext_item", None),
		getattr(doc, "fuel_type", None),
		getattr(doc, "brand", None),
	)
	resolved_company = company or getattr(doc, "company", None) or _get_default_company()

	unresolved = []
	if not resolved_item_code:
		unresolved.append("No canonical ERPNext Item could be resolved for this fuel purchase.")
	if not resolved_company:
		unresolved.append("No ERPNext Company could be resolved for this fuel purchase.")

	item_uom = None
	if resolved_item_code:
		item_uom = frappe.db.get_value("Item", resolved_item_code, "stock_uom")

	payload = {
		"doctype": "Purchase Invoice",
		"supplier": doc.supplier,
		"posting_date": doc.dated,
		"company": resolved_company,
		"bill_no": doc.code,
		"items": [
			{
				"item_code": resolved_item_code,
				"qty": flt(doc.actual_quantity),
				"uom": item_uom or getattr(doc, "unit_of_measure", None),
				"stock_uom": item_uom,
				"rate": flt(doc.unit_cost),
				"amount": flt(doc.total_cost),
			}
		],
		"remarks": f"Mapped from Fuel Purchase {getattr(doc, 'name', 'unsaved')} / {doc.code}",
	}
	return payload, unresolved


def _build_inventory_receipt_purchase_receipt_payload(doc, company=None, warehouse=None, item_code=None):
	resolved_item_code = item_code or _find_item_code(
		getattr(doc, "item_code", None),
		getattr(doc, "erpnext_item", None),
		getattr(doc, "product", None),
		getattr(doc, "brand", None),
	)
	resolved_company = company or getattr(doc, "company", None) or _get_default_company()
	resolved_warehouse = _resolve_stock_warehouse(
		resolved_company,
		item_code=resolved_item_code,
		warehouse=warehouse or getattr(doc, "warehouse", None),
	)

	unresolved = []
	if not resolved_item_code:
		unresolved.append("No canonical ERPNext Item could be resolved for this inventory receipt.")
	if not resolved_company:
		unresolved.append("No ERPNext Company could be resolved for this inventory receipt.")
	if not resolved_warehouse:
		unresolved.append(_warehouse_resolution_message("this inventory receipt", resolved_company))

	item_uom = None
	if resolved_item_code:
		item_uom = frappe.db.get_value("Item", resolved_item_code, "stock_uom")

	qty = flt(doc.units) * max(int(getattr(doc, "subunits_per_unit", 0) or 1), 1)
	rate = flt(getattr(doc, "subunit_cost", 0) or getattr(doc, "unit_cost", 0))

	payload = {
		"doctype": "Purchase Receipt",
		"supplier": doc.supplier,
		"posting_date": doc.dated,
		"company": resolved_company,
		"set_warehouse": resolved_warehouse,
		"supplier_delivery_note": doc.code,
		"items": [
			{
				"item_code": resolved_item_code,
				"qty": qty,
				"uom": item_uom or getattr(doc, "unit_of_measure", None),
				"stock_uom": item_uom,
				"warehouse": resolved_warehouse,
				"rate": rate,
				"amount": flt(doc.total_cost),
			}
		],
		"remarks": f"Mapped from Inventory Receipt {getattr(doc, 'name', 'unsaved')} / {doc.code}",
	}
	return payload, unresolved


def _build_inventory_receipt_purchase_invoice_payload(doc, company=None, item_code=None):
	resolved_item_code = item_code or _find_item_code(
		getattr(doc, "item_code", None),
		getattr(doc, "erpnext_item", None),
		getattr(doc, "product", None),
		getattr(doc, "brand", None),
	)
	resolved_company = company or getattr(doc, "company", None) or _get_default_company()

	unresolved = []
	if not resolved_item_code:
		unresolved.append("No canonical ERPNext Item could be resolved for this inventory receipt.")
	if not resolved_company:
		unresolved.append("No ERPNext Company could be resolved for this inventory receipt.")

	item_uom = None
	if resolved_item_code:
		item_uom = frappe.db.get_value("Item", resolved_item_code, "stock_uom")

	qty = flt(doc.units) * max(int(getattr(doc, "subunits_per_unit", 0) or 1), 1)
	rate = flt(getattr(doc, "subunit_cost", 0) or getattr(doc, "unit_cost", 0))

	payload = {
		"doctype": "Purchase Invoice",
		"supplier": doc.supplier,
		"posting_date": doc.dated,
		"company": resolved_company,
		"bill_no": doc.code,
		"items": [
			{
				"item_code": resolved_item_code,
				"qty": qty,
				"uom": item_uom or getattr(doc, "unit_of_measure", None),
				"stock_uom": item_uom,
				"rate": rate,
				"amount": flt(doc.total_cost),
			}
		],
		"remarks": f"Mapped from Inventory Receipt {getattr(doc, 'name', 'unsaved')} / {doc.code}",
	}
	return payload, unresolved


def _build_sales_entry_sales_invoice_payload(doc, company=None):
	resolved_company = company or getattr(doc, "company", None) or _get_default_company()
	unresolved = []

	item_rows = _sales_entry_items(doc)
	unresolved.extend([msg for row in item_rows for msg in row.pop("unresolved_dependencies", [])])

	if not getattr(doc, "customer", None):
		unresolved.append("Customer is required to create a Sales Invoice.")
	if not resolved_company:
		unresolved.append("No ERPNext Company could be resolved for this sales entry.")

	if not item_rows:
		item_rows = [
			{
				"item_code": None,
				"qty": 1,
				"rate": flt(doc.amount),
				"amount": flt(doc.amount),
				"description": f"Operational {doc.sale_type} sale captured from Sales Entry",
			}
		]
		unresolved.append("Sales Entry has no line items; a canonical ERPNext Item is still required for posting.")

	for row in item_rows:
		item_code = row.get("item_code")
		if item_code and _is_stock_item(item_code):
			row["warehouse"] = _resolve_stock_warehouse(
				resolved_company,
				item_code=item_code,
				warehouse=row.get("warehouse"),
			)
			if not row.get("warehouse"):
				unresolved.append(
					f"No ERPNext Warehouse could be resolved for stock item {item_code} in company {resolved_company}."
				)

	sales_invoice = {
		"doctype": "Sales Invoice",
		"customer": getattr(doc, "customer", None),
		"posting_date": doc.dated,
		"company": resolved_company,
		"is_pos": 0 if getattr(doc, "payment_method", None) == "Credit" else 1,
		"update_stock": 0,
		"items": item_rows,
		"remarks": f"Mapped from Sales Entry {getattr(doc, 'name', 'unsaved')}",
	}
	return sales_invoice, unresolved


def _fuel_purchase_targets(doc):
	purchase_receipt, unresolved = _build_fuel_purchase_purchase_receipt_payload(doc)
	purchase_invoice, invoice_unresolved = _build_fuel_purchase_purchase_invoice_payload(
		doc, company=purchase_receipt.get("company"), item_code=purchase_receipt["items"][0]["item_code"]
	)

	targets = [
		{
			"target_doctype": "Purchase Receipt",
			"recommended": True,
			"payload": purchase_receipt,
			"unresolved_dependencies": unresolved,
		},
			{
				"target_doctype": "Purchase Invoice",
				"recommended": True,
				"payload": purchase_invoice,
				"unresolved_dependencies": invoice_unresolved,
			},
		]

	if flt(getattr(doc, "amount_paid", 0)) > 0:
		targets.append(
			{
				"target_doctype": "Payment Entry",
				"recommended": True,
				"payload": {
					"doctype": "Payment Entry",
					"payment_type": "Pay",
					"party_type": "Supplier",
					"party": doc.supplier,
					"posting_date": doc.dated,
					"paid_amount": flt(doc.amount_paid),
					"mode_of_payment": _payment_mode(getattr(doc, "payment_method", None)),
					"remarks": f"Settlement for Fuel Purchase {doc.code}",
				},
				"unresolved_dependencies": []
				if _payment_mode(getattr(doc, "payment_method", None))
				else ["Payment method does not map to a standard ERPNext Mode of Payment."],
			}
		)

	return targets


def _inventory_receipt_targets(doc):
	purchase_receipt, unresolved = _build_inventory_receipt_purchase_receipt_payload(doc)
	purchase_invoice, invoice_unresolved = _build_inventory_receipt_purchase_invoice_payload(
		doc,
		company=purchase_receipt.get("company"),
		item_code=purchase_receipt["items"][0]["item_code"],
	)

	targets = [
		{
				"target_doctype": "Purchase Receipt",
				"recommended": True,
				"payload": purchase_receipt,
				"unresolved_dependencies": unresolved,
			},
			{
				"target_doctype": "Purchase Invoice",
				"recommended": True,
				"payload": purchase_invoice,
				"unresolved_dependencies": invoice_unresolved,
			},
		]

	if flt(getattr(doc, "amount_paid", 0)) > 0:
		targets.append(
			{
				"target_doctype": "Payment Entry",
				"recommended": True,
				"payload": {
					"doctype": "Payment Entry",
					"payment_type": "Pay",
					"party_type": "Supplier",
					"party": doc.supplier,
					"posting_date": doc.dated,
					"paid_amount": flt(doc.amount_paid),
					"mode_of_payment": _payment_mode(getattr(doc, "payment_method", None)),
					"remarks": f"Settlement for Inventory Receipt {doc.code}",
				},
				"unresolved_dependencies": []
				if _payment_mode(getattr(doc, "payment_method", None))
				else ["Payment method does not map to a standard ERPNext Mode of Payment."],
			}
		)

	return targets


def _sales_entry_items(doc):
	items = []
	for row in getattr(doc, "items", []) or []:
		item_code = _find_item_code(
			getattr(row, "item_code", None),
			getattr(row, "erpnext_item", None),
			getattr(row, "product", None),
		)
		unresolved = []
		if not item_code:
			unresolved.append(
				f"Could not resolve ERPNext Item for sales row product {getattr(row, 'product', 'Unknown')}."
			)
		items.append(
			{
				"item_code": item_code,
				"qty": flt(getattr(row, "quantity", 0)),
				"rate": flt(getattr(row, "unit_price", 0)),
				"amount": flt(getattr(row, "total_amount", 0)),
				"unresolved_dependencies": unresolved,
			}
		)
	return items


def _sales_entry_targets(doc):
	sales_invoice, unresolved = _build_sales_entry_sales_invoice_payload(doc)

	targets = [
		{
			"target_doctype": "Sales Invoice",
			"recommended": True,
			"payload": sales_invoice,
			"unresolved_dependencies": unresolved,
		}
	]

	if getattr(doc, "payment_method", None) != "Credit":
		targets.append(
			{
				"target_doctype": "Payment Entry",
				"recommended": True,
				"payload": {
					"doctype": "Payment Entry",
					"payment_type": "Receive",
					"party_type": "Customer",
					"party": getattr(doc, "customer", None),
					"posting_date": doc.dated,
					"received_amount": flt(doc.amount),
					"mode_of_payment": _payment_mode(getattr(doc, "payment_method", None)),
					"remarks": f"Settlement for Sales Entry {getattr(doc, 'name', 'unsaved')}",
				},
				"unresolved_dependencies": []
				if getattr(doc, "customer", None) and _payment_mode(getattr(doc, "payment_method", None))
				else [
					msg
					for msg in [
						None
						if getattr(doc, "customer", None)
						else "Customer is required to allocate the payment in ERPNext.",
						None
						if _payment_mode(getattr(doc, "payment_method", None))
						else "Payment method does not map to a standard ERPNext Mode of Payment.",
					]
					if msg
				],
			}
		)

	return targets


@frappe.whitelist()
def get_operational_mapping_bundle():
	"""Return supported operational source doctypes and their ERPNext targets."""
	return OPERATIONAL_MAPPING_BUNDLE


@frappe.whitelist()
def preview_erpnext_mapping(source_doctype, docname=None, doc=None):
	"""Preview how an operational National Oil document should map into ERPNext doctypes."""
	source_doc = _coerce_source_doc(source_doctype, docname=docname, doc=doc)

	if source_doctype == "Fuel Purchase":
		targets = _fuel_purchase_targets(source_doc)
	elif source_doctype == "Inventory Receipt":
		targets = _inventory_receipt_targets(source_doc)
	elif source_doctype == "Sales Entry":
		targets = _sales_entry_targets(source_doc)
	else:
		frappe.throw(frappe._("Unsupported source doctype {0}").format(source_doctype))

	return {
		"source_doctype": source_doctype,
		"source_name": getattr(source_doc, "name", None),
		"targets": targets,
	}


@frappe.whitelist()
def create_erpnext_target_from_operational(
	source_doctype,
	target_doctype,
	docname=None,
	doc=None,
	company=None,
	warehouse=None,
	item_code=None,
	submit=0,
):
	"""Create a controlled ERPNext target document from an operational National Oil record."""
	source_doc = _coerce_source_doc(source_doctype, docname=docname, doc=doc)
	submit = cint(submit)

	if source_doctype == "Fuel Purchase" and target_doctype == "Purchase Receipt":
		payload, unresolved = _build_fuel_purchase_purchase_receipt_payload(
			source_doc,
			company=company,
			warehouse=warehouse,
			item_code=item_code,
		)
	elif source_doctype == "Fuel Purchase" and target_doctype == "Purchase Invoice":
		payload, unresolved = _build_fuel_purchase_purchase_invoice_payload(
			source_doc,
			company=company,
			item_code=item_code,
		)
	elif source_doctype == "Inventory Receipt" and target_doctype == "Purchase Receipt":
		payload, unresolved = _build_inventory_receipt_purchase_receipt_payload(
			source_doc,
			company=company,
			warehouse=warehouse,
			item_code=item_code,
		)
	elif source_doctype == "Inventory Receipt" and target_doctype == "Purchase Invoice":
		payload, unresolved = _build_inventory_receipt_purchase_invoice_payload(
			source_doc,
			company=company,
			item_code=item_code,
		)
	elif source_doctype == "Sales Entry" and target_doctype == "Sales Invoice":
		payload, unresolved = _build_sales_entry_sales_invoice_payload(
			source_doc,
			company=company,
		)
	else:
		frappe.throw(
			frappe._("Creation flow from {0} to {1} is not implemented yet").format(
				source_doctype, target_doctype
			)
		)

	if unresolved:
		frappe.throw("\n".join(unresolved))

	frappe.has_permission(target_doctype, "create", throw=True)
	if submit:
		frappe.has_permission(target_doctype, "submit", throw=True)

	target_doc = frappe.get_doc(payload)
	target_doc.insert(ignore_permissions=True)
	if submit:
		target_doc.submit()

	return {
		"target_doctype": target_doctype,
		"name": target_doc.name,
		"docstatus": target_doc.docstatus,
	}


@frappe.whitelist()
def create_payment_entry_for_reference(
	reference_doctype,
	reference_name,
	mode_of_payment=None,
	payment_method=None,
	posting_date=None,
	submit=0,
):
	"""Create a draft or submitted Payment Entry from an ERPNext source document."""
	submit = cint(submit)
	frappe.has_permission(reference_doctype, "read", throw=True)
	source_doc = frappe.get_doc(reference_doctype, reference_name)
	if source_doc.docstatus != 1:
		frappe.throw(
			frappe._("{0} {1} must be submitted before creating a Payment Entry.").format(
				reference_doctype, reference_name
			)
		)
	company = source_doc.get("company")

	resolved_mode, bank_account = _resolve_mode_of_payment(
		company, payment_method=payment_method, mode_of_payment=mode_of_payment
	)

	if not bank_account:
		frappe.throw(
			frappe._(
				"No Mode of Payment Account is configured for the selected payment mode and company."
			)
		)

	frappe.has_permission("Payment Entry", "create", throw=True)
	if submit:
		frappe.has_permission("Payment Entry", "submit", throw=True)

	pe = get_payment_entry(
		reference_doctype,
		reference_name,
		bank_account=bank_account,
		reference_date=posting_date or source_doc.get("posting_date"),
		ignore_permissions=True,
	)
	pe.mode_of_payment = resolved_mode
	if posting_date:
		pe.posting_date = posting_date
	pe.insert(ignore_permissions=True)
	if submit:
		pe.submit()

	return {
		"target_doctype": "Payment Entry",
		"name": pe.name,
		"docstatus": pe.docstatus,
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
	}
