import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if "hrms" not in frappe.get_installed_apps():
		return

	create_custom_fields(
		{
			"Shift Assignment": [
				{
					"fieldname": "assigned_pumps",
					"fieldtype": "Table",
					"label": "Assigned Pumps",
					"options": "Shift Assigned Pump",
					"insert_after": "shift_schedule_assignment",
				},
				{
					"fieldname": "total_expected_sales",
					"fieldtype": "Currency",
					"label": "Total Expected Sales",
					"read_only": 1,
					"insert_after": "assigned_pumps",
				},
				{
					"fieldname": "closed_at",
					"fieldtype": "Datetime",
					"label": "Closed At",
					"read_only": 1,
					"insert_after": "total_expected_sales",
				},
				{
					"fieldname": "reconciliation_status",
					"fieldtype": "Select",
					"label": "Reconciliation Status",
					"options": "Open\nClosed\nVerified",
					"default": "Open",
					"read_only": 1,
					"insert_after": "closed_at",
				},
			]
		},
		update=True,
	)
