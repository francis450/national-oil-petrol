import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PumpReading(Document):
	def validate(self):
		if flt(self.closing_reading) < flt(self.opening_reading):
			frappe.throw(frappe._("Closing Reading cannot be less than Opening Reading"))

		self.variance = flt(self.closing_reading) - flt(self.opening_reading)

		# Prevent duplicate reading for same pump on same date
		existing = frappe.db.exists(
			"Pump Reading",
			{
				"pump_number": self.pump_number,
				"dated": self.dated,
				"name": ("!=", self.name),
			},
		)
		if existing:
			frappe.throw(
				frappe._("A reading for {0} on {1} already exists").format(
					self.pump_number, self.dated
				)
			)
