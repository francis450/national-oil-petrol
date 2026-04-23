import frappe
from frappe.utils import cint, flt


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
	"Bank Transfer": "Bank Transfer",
	"Credit": None,
}


def _coerce_source_doc(source_doctype, docname=None, doc=None):
	if source_doctype not in OPERATIONAL_MAPPING_BUNDLE:
		frappe.throw(frappe._("Unsupported source doctype {0}").format(source_doctype))

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


def _get_default_company():
	return (
		frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_value("Company", {}, "name")
	)


def _get_default_warehouse():
	return frappe.db.get_value("Warehouse", {"is_group": 0}, "name")


def _get_item_default_warehouse(item_code):
	return (
		frappe.db.get_value("Item Default", {"parent": item_code}, "default_warehouse")
		or _get_default_warehouse()
	)


def _build_fuel_purchase_purchase_receipt_payload(doc, company=None, warehouse=None, item_code=None):
	resolved_item_code = item_code or _find_item_code(
		getattr(doc, "item_code", None),
		getattr(doc, "erpnext_item", None),
		getattr(doc, "fuel_type", None),
		getattr(doc, "brand", None),
	)
	resolved_company = company or getattr(doc, "company", None) or _get_default_company()
	resolved_warehouse = warehouse or getattr(doc, "warehouse", None)
	if resolved_item_code and not resolved_warehouse:
		resolved_warehouse = _get_item_default_warehouse(resolved_item_code)

	unresolved = []
	if not resolved_item_code:
		unresolved.append("No canonical ERPNext Item could be resolved for this fuel purchase.")
	if not resolved_company:
		unresolved.append("No ERPNext Company could be resolved for this fuel purchase.")
	if not resolved_warehouse:
		unresolved.append("No ERPNext Warehouse could be resolved for this fuel purchase.")

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


def _fuel_purchase_targets(doc):
	purchase_receipt, unresolved = _build_fuel_purchase_purchase_receipt_payload(doc)
	item_code = purchase_receipt["items"][0]["item_code"]
	resolved_company = purchase_receipt.get("company")

	purchase_invoice = {
		"doctype": "Purchase Invoice",
		"supplier": doc.supplier,
		"posting_date": doc.dated,
		"company": resolved_company,
		"bill_no": doc.code,
		"items": [
			{
				"item_code": item_code,
				"qty": flt(doc.actual_quantity),
				"uom": purchase_receipt["items"][0].get("uom"),
				"stock_uom": purchase_receipt["items"][0].get("stock_uom"),
				"rate": flt(doc.unit_cost),
				"amount": flt(doc.total_cost),
			}
		],
		"remarks": f"Mapped from Fuel Purchase {getattr(doc, 'name', 'unsaved')} / {doc.code}",
	}

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
			"unresolved_dependencies": unresolved,
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
	item_code = _find_item_code(
		getattr(doc, "item_code", None),
		getattr(doc, "erpnext_item", None),
		getattr(doc, "product", None),
		getattr(doc, "brand", None),
	)
	unresolved = []
	if not item_code:
		unresolved.append("No canonical ERPNext Item could be resolved for this inventory receipt.")

	qty = flt(doc.units) * max(int(getattr(doc, "subunits_per_unit", 0) or 1), 1)
	rate = flt(getattr(doc, "subunit_cost", 0) or getattr(doc, "unit_cost", 0))

	targets = [
		{
			"target_doctype": "Purchase Receipt",
			"recommended": True,
			"payload": {
				"doctype": "Purchase Receipt",
				"supplier": doc.supplier,
				"posting_date": doc.dated,
				"supplier_delivery_note": doc.code,
				"items": [{"item_code": item_code, "qty": qty, "uom": doc.unit_of_measure, "rate": rate}],
				"remarks": f"Mapped from Inventory Receipt {getattr(doc, 'name', 'unsaved')} / {doc.code}",
			},
			"unresolved_dependencies": unresolved,
		},
		{
			"target_doctype": "Purchase Invoice",
			"recommended": True,
			"payload": {
				"doctype": "Purchase Invoice",
				"supplier": doc.supplier,
				"posting_date": doc.dated,
				"bill_no": doc.code,
				"items": [{"item_code": item_code, "qty": qty, "uom": doc.unit_of_measure, "rate": rate}],
				"remarks": f"Mapped from Inventory Receipt {getattr(doc, 'name', 'unsaved')} / {doc.code}",
			},
			"unresolved_dependencies": unresolved,
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
	item_rows = _sales_entry_items(doc)
	unresolved = [msg for row in item_rows for msg in row.pop("unresolved_dependencies", [])]

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

	sales_invoice = {
		"doctype": "Sales Invoice",
		"customer": getattr(doc, "customer", None),
		"posting_date": doc.dated,
		"is_pos": 0 if getattr(doc, "payment_method", None) == "Credit" else 1,
		"items": item_rows,
		"remarks": f"Mapped from Sales Entry {getattr(doc, 'name', 'unsaved')}",
	}

	targets = [
		{
			"target_doctype": "Sales Invoice",
			"recommended": True,
			"payload": sales_invoice,
			"unresolved_dependencies": unresolved + (
				["Customer is required to create a Sales Invoice."]
				if not getattr(doc, "customer", None)
				else []
			),
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
	else:
		frappe.throw(
			frappe._("Creation flow from {0} to {1} is not implemented yet").format(
				source_doctype, target_doctype
			)
		)

	if unresolved:
		frappe.throw("\n".join(unresolved))

	target_doc = frappe.get_doc(payload)
	target_doc.insert(ignore_permissions=True)
	if submit:
		target_doc.submit()

	return {
		"target_doctype": target_doctype,
		"name": target_doc.name,
		"docstatus": target_doc.docstatus,
	}
