frappe.query_reports["Daily Sales Summary"] = {
	filters: [
		{
			fieldname: "dated",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "sale_type",
			label: __("Sale Type"),
			fieldtype: "Select",
			options: "\nWet Stock\nOther",
		},
	],
};
