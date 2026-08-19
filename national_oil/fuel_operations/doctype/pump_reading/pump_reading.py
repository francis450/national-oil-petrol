import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, now

# Ported from nog_erpnext/forecourt/utils.py — proven 4-pump / 13-nozzle layout.
# Nozzle -> canonical ERPNext Item code (fuel tank).
NOZZLE_ITEM = {
	1: "PETROL", 2: "DIESEL", 3: "PETROL", 4: "DIESEL",
	5: "PETROL", 6: "DIESEL", 7: "PETROL", 8: "DIESEL",
	9: "PETROL", 10: "DIESEL", 11: "PETROL", 12: "DIESEL",
	13: "PARAFFIN",
}

NOZZLE_PUMP = {
	1: "1", 2: "1", 3: "1", 4: "1",
	5: "2", 6: "2", 7: "2", 8: "2",
	9: "3", 10: "3", 11: "3", 12: "3",
	13: "4",
}


class PumpReading(Document):
	def validate(self):
		self.set_nozzle_defaults()
		if self.docstatus == 1 and not self.closing_reading:
			frappe.throw(_("Closing Reading is required to submit."))
		self.validate_meter_values()
		self.calculate_totals()
		self.set_unit_price()
		self.calculate_expected_sales()
		self.validate_no_duplicate()

	def on_submit(self):
		self.close_out_shift()

	def close_out_shift(self):
		if not self.shift:
			return

		shift_doc = frappe.get_doc("Shift Assignment", self.shift)
		matched = False
		for row in shift_doc.assigned_pumps:
			if cint(row.nozzle_no) == cint(self.nozzle_no):
				row.status = "Closed"
				matched = True
				break

		if not matched or not shift_doc.assigned_pumps:
			return

		all_closed = all(row.status == "Closed" for row in shift_doc.assigned_pumps)
		if all_closed:
			total_expected_sales = frappe.db.sql(
				"""
				select sum(expected_sales_amount)
				from `tabPump Reading`
				where shift = %s and docstatus = 1
				""",
				self.shift,
			)[0][0]
			shift_doc.total_expected_sales = flt(total_expected_sales)
			shift_doc.closed_at = now()
			shift_doc.reconciliation_status = "Closed"

		shift_doc.save(ignore_permissions=True)

	def set_nozzle_defaults(self):
		nozzle_no = cint(self.nozzle_no)
		fuel_item = NOZZLE_ITEM.get(nozzle_no)
		pump_no = NOZZLE_PUMP.get(nozzle_no)

		if not fuel_item or not pump_no:
			frappe.throw(_("Nozzle number must be between 1 and 13."))

		self.pump_no = pump_no
		self.pump_number = f"P{pump_no}"

		expected_fuel_type = frappe.db.get_value("Fuel Type", {"item": fuel_item}, "name")
		if self.fuel_type and expected_fuel_type and self.fuel_type != expected_fuel_type:
			frappe.throw(
				_("Nozzle {0} is configured for {1}, but this reading uses {2}.").format(
					nozzle_no, frappe.bold(expected_fuel_type), frappe.bold(self.fuel_type)
				)
			)
		if not self.fuel_type and expected_fuel_type:
			self.fuel_type = expected_fuel_type

	def validate_meter_values(self):
		if not self.closing_reading:
			return

		opening = flt(self.opening_reading)
		closing = flt(self.closing_reading)

		if closing >= opening:
			return

		if not self.meter_rollover:
			frappe.throw(
				_(
					"Closing Reading {0} cannot be less than Opening Reading {1}. "
					"If the physical meter rolled over, tick Meter Rollover and set the Rollover Limit."
				).format(closing, opening)
			)

		if flt(self.meter_rollover_limit) <= opening:
			frappe.throw(_("Rollover Limit must be greater than Opening Reading when Meter Rollover is ticked."))

	def calculate_totals(self):
		if not self.closing_reading:
			self.variance = 0
			return

		opening = flt(self.opening_reading)
		closing = flt(self.closing_reading)

		if self.meter_rollover and closing < opening:
			self.variance = flt(self.meter_rollover_limit) - opening + closing
		else:
			self.variance = closing - opening

	def set_unit_price(self):
		if self.unit_price or not self.fuel_type:
			return

		price = frappe.db.sql(
			"""
			select selling_price_retail
			from `tabFuel Price`
			where fuel_type = %s and effective_date <= %s
			order by effective_date desc
			limit 1
			""",
			(self.fuel_type, self.dated),
		)
		if price:
			self.unit_price = flt(price[0][0])

	def calculate_expected_sales(self):
		self.expected_sales_amount = flt(self.variance) * flt(self.unit_price)

	def validate_no_duplicate(self):
		existing = frappe.db.exists(
			"Pump Reading",
			{
				"nozzle_no": self.nozzle_no,
				"dated": self.dated,
				"shift": self.shift,
				"name": ("!=", self.name),
			},
		)
		if existing:
			frappe.throw(
				_("A reading for Nozzle {0} on {1} ({2} shift) already exists").format(
					self.nozzle_no, self.dated, self.shift
				)
			)


@frappe.whitelist()
def get_nozzle_defaults(nozzle_no):
	frappe.has_permission("Pump Reading", "read", throw=True)
	nozzle_no = cint(nozzle_no)
	fuel_item = NOZZLE_ITEM.get(nozzle_no)
	pump_no = NOZZLE_PUMP.get(nozzle_no)
	if not fuel_item or not pump_no:
		return None

	fuel_type = frappe.db.get_value("Fuel Type", {"item": fuel_item}, "name")
	return {"nozzle_no": nozzle_no, "pump_no": pump_no, "fuel_type": fuel_type, "item": fuel_item}
