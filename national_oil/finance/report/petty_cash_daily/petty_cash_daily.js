frappe.query_reports["Petty Cash — Daily"] = {
	filters: [
		{
			fieldname: "dated",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
	],
};
