frappe.query_reports["Attendance Summary"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Int",
			default: new Date().getFullYear(),
			reqd: 1,
		},
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options:
				"1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12",
			default: String(new Date().getMonth() + 1),
			reqd: 1,
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "NO Employee",
		},
	],
};
