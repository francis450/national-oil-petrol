import frappe
from frappe import _
from frappe.utils import today, add_days, getdate


@frappe.whitelist()
def get_dashboard_metrics():
	"""Single call returning all KPIs for the dashboard."""
	t = today()

	# Sales totals
	def sales_sum(from_date, to_date=None):
		filters = [
			["Sales Entry", "docstatus", "=", 1],
			["Sales Entry", "dated", ">=", from_date],
		]
		if to_date:
			filters.append(["Sales Entry", "dated", "<=", to_date])
		return frappe.db.get_value("Sales Entry", filters, "sum(amount)") or 0

	today_sales = sales_sum(t)
	month_start = getdate(t).replace(day=1).strftime("%Y-%m-%d")
	month_sales = sales_sum(month_start, t)
	year_start = getdate(t).replace(month=1, day=1).strftime("%Y-%m-%d")
	year_sales = sales_sum(year_start, t)

	# Fuel stock per fuel type
	fuel_stock = frappe.db.sql("""
		SELECT p.product_name, p.quantity, ft.unit_of_measure
		FROM `tabProduct` p
		LEFT JOIN `tabFuel Type` ft ON ft.name = p.fuel_type
		WHERE p.is_fuel = 1
	""", as_dict=True)

	# Outstanding debts summary
	debt_summary = frappe.db.sql("""
		SELECT COUNT(*) as open_count, SUM(balance) as total_outstanding
		FROM `tabCustomer Debt`
		WHERE docstatus = 1 AND status IN ('Open', 'Partially Paid')
	""", as_dict=True)[0]

	return {
		"today_sales": today_sales,
		"month_sales": month_sales,
		"year_sales": year_sales,
		"fuel_stock": fuel_stock,
		"open_debts": debt_summary.get("open_count") or 0,
		"total_outstanding": debt_summary.get("total_outstanding") or 0,
	}


@frappe.whitelist()
def get_sales_trend(days=7):
	"""Get sales trend for the last N days."""
	t = today()
	start_date = add_days(t, -int(days))

	sales_data = frappe.db.sql("""
		SELECT DATE(dated) as date, SUM(amount) as amount, COUNT(*) as count
		FROM `tabSales Entry`
		WHERE docstatus = 1 AND dated >= %s AND dated <= %s
		GROUP BY DATE(dated)
		ORDER BY dated ASC
	""", (start_date, t), as_dict=True)

	return {
		"labels": [row["date"].strftime("%Y-%m-%d") for row in sales_data],
		"data": [row["amount"] for row in sales_data],
		"count": [row["count"] for row in sales_data],
	}


@frappe.whitelist()
def get_sales_trend(days=7):
	"""Daily sales totals for last N days, split by sale_type."""
	days = int(days)
	from_date = add_days(today(), -days + 1)
	rows = frappe.db.sql("""
		SELECT dated, sale_type, SUM(amount) as total
		FROM `tabSales Entry`
		WHERE docstatus = 1 AND dated >= %s
		GROUP BY dated, sale_type
		ORDER BY dated ASC
	""", from_date, as_dict=True)
	return rows
