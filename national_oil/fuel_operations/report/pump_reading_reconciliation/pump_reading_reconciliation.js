frappe.query_reports["Pump Reading Reconciliation"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "reconciliation_status",
			label: __("Reconciliation Status"),
			fieldtype: "Select",
			options: "\nOpen\nClosed\nVerified",
		},
	],
};
