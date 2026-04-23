frappe.query_reports["Fuel Stock Summary"] = {
	filters: [
		{
			fieldname: "fuel_type",
			label: __("Fuel Type"),
			fieldtype: "Link",
			options: "Fuel Type",
		},
	],
};
