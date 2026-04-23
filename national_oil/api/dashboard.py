import frappe
from frappe.utils import add_days, cint, flt, getdate, nowdate, today


PIPELINE_DOCTYPES = ("Fuel Purchase", "Inventory Receipt", "Sales Entry")


def _doctype_exists(doctype):
	return bool(frappe.db.exists("DocType", doctype))


def _sum_field(doctype, fieldname, filters=None):
	if not _doctype_exists(doctype):
		return 0
	return flt(frappe.db.get_value(doctype, filters or {}, f"sum({fieldname})") or 0)


def _count_docs(doctype, filters=None):
	if not _doctype_exists(doctype):
		return 0
	return cint(frappe.db.count(doctype, filters=filters or {}))


def _month_start(date_value=None):
	reference_date = getdate(date_value or today())
	return reference_date.replace(day=1).strftime("%Y-%m-%d")


def _sales_totals():
	current_day = today()
	month_start = _month_start(current_day)

	today_sales = _sum_field(
		"Sales Invoice",
		"grand_total",
		{"docstatus": 1, "posting_date": current_day},
	)
	month_sales = _sum_field(
		"Sales Invoice",
		"grand_total",
		{"docstatus": 1, "posting_date": ["between", [month_start, current_day]]},
	)
	return today_sales, month_sales


def _outstanding_summary():
	return {
		"receivables": _sum_field("Sales Invoice", "outstanding_amount", {"docstatus": 1}),
		"payables": _sum_field("Purchase Invoice", "outstanding_amount", {"docstatus": 1}),
	}


def _stock_summary():
	if not frappe.db.table_exists("Bin") or not _doctype_exists("Item"):
		return {"total_qty": 0, "levels": []}

	rows = frappe.db.sql(
		"""
		select
			i.item_name as label,
			sum(b.actual_qty) as value
		from `tabBin` b
		inner join `tabItem` i on i.name = b.item_code
		where i.is_stock_item = 1
		group by i.name, i.item_name
		having sum(b.actual_qty) > 0
		order by value desc, label asc
		limit 5
		""",
		as_dict=True,
	)

	total_qty = frappe.db.sql(
		"""
		select sum(actual_qty)
		from `tabBin`
		""",
	)[0][0] or 0

	colors = [
		"bg-deepseek-blue",
		"bg-bioluminescent-green",
		"bg-yellow-500",
		"bg-pink-500",
		"bg-sky-500",
	]

	levels = []
	for idx, row in enumerate(rows):
		levels.append(
			{
				"label": row.get("label") or "Unnamed Item",
				"value": flt(row.get("value")),
				"color": colors[idx % len(colors)],
			}
		)

	return {"total_qty": flt(total_qty), "levels": levels}


def _attendance_summary():
	if not _doctype_exists("Attendance"):
		return [{"label": "Present", "value": 0}, {"label": "Absent", "value": 0}]

	rows = frappe.db.sql(
		"""
		select status, count(*) as value
		from `tabAttendance`
		where attendance_date = %s
		group by status
		""",
		nowdate(),
		as_dict=True,
	)
	status_counts = {row.status: cint(row.value) for row in rows}
	present = status_counts.get("Present", 0)
	absent = sum(value for status, value in status_counts.items() if status != "Present")
	return [
		{"label": "Present", "value": present, "color": "bg-bioluminescent-green"},
		{"label": "Absent", "value": absent, "color": "bg-alert-magenta"},
	]


def _pipeline_summary():
	colors = {
		"Fuel Purchase": "bg-deepseek-blue",
		"Inventory Receipt": "bg-yellow-500",
		"Sales Entry": "bg-bioluminescent-green",
	}
	rows = []
	for doctype in PIPELINE_DOCTYPES:
		rows.append(
			{
				"label": doctype,
				"value": _count_docs(doctype),
				"color": colors.get(doctype, "bg-gray-500"),
			}
		)
	return rows


def _settlement_summary():
	current_day = today()
	month_start = _month_start(current_day)
	if not _doctype_exists("Payment Entry"):
		return {"receipts_this_month": 0, "payments_this_month": 0}

	rows = frappe.db.sql(
		"""
		select payment_type, sum(ifnull(received_amount, 0)) as received_amount, sum(ifnull(paid_amount, 0)) as paid_amount
		from `tabPayment Entry`
		where docstatus = 1 and posting_date between %s and %s
		group by payment_type
		""",
		(month_start, current_day),
		as_dict=True,
	)
	summary = {"receipts_this_month": 0, "payments_this_month": 0}
	for row in rows:
		if row.payment_type == "Receive":
			summary["receipts_this_month"] = flt(row.received_amount)
		elif row.payment_type == "Pay":
			summary["payments_this_month"] = flt(row.paid_amount)
	return summary


@frappe.whitelist()
def get_sales_trend(days=7):
	"""Return posted ERPNext sales invoice totals for the last N days."""
	days = max(cint(days or 7), 1)
	current_day = getdate(today())
	start_date = add_days(current_day, -days + 1)

	if not _doctype_exists("Sales Invoice"):
		return []

	rows = frappe.db.sql(
		"""
		select posting_date, sum(grand_total) as total
		from `tabSales Invoice`
		where docstatus = 1 and posting_date between %s and %s
		group by posting_date
		order by posting_date asc
		""",
		(start_date, current_day),
		as_dict=True,
	)
	by_date = {row.posting_date.strftime("%Y-%m-%d"): flt(row.total) for row in rows}

	trend = []
	for offset in range(days):
		date_value = add_days(start_date, offset)
		label = getdate(date_value).strftime("%b %d")
		key = getdate(date_value).strftime("%Y-%m-%d")
		trend.append({"label": label, "value": by_date.get(key, 0)})
	return trend


@frappe.whitelist()
def get_dashboard_metrics():
	"""Return dashboard KPIs based on canonical ERPNext docs plus operational backlog counts."""
	today_sales, month_sales = _sales_totals()
	outstanding = _outstanding_summary()
	stock = _stock_summary()
	pipeline = _pipeline_summary()
	settlement = _settlement_summary()

	return {
		"today_sales": today_sales,
		"month_sales": month_sales,
		"outstanding_receivables": outstanding["receivables"],
		"outstanding_payables": outstanding["payables"],
		"stock_balance_qty": stock["total_qty"],
		"operational_backlog": sum(row["value"] for row in pipeline),
		"sales_trend": get_sales_trend(7),
		"stock_levels": stock["levels"],
		"attendance": _attendance_summary(),
		"pipeline": pipeline,
		"settlement": settlement,
	}
