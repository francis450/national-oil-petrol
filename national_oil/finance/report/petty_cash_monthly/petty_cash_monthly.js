frappe.query_reports["Petty Cash — Monthly"] = {
	filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Int",
			default: new Date().getFullYear(),
		},
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options:
				"\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12",
		},
	],
};
