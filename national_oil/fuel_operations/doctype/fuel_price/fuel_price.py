import frappe
from frappe.model.document import Document


class FuelPrice(Document):
	def before_save(self):
		self.set_by = frappe.session.user

	def validate(self):
		existing = frappe.db.exists(
			"Fuel Price",
			{
				"fuel_type": self.fuel_type,
				"effective_date": self.effective_date,
				"name": ("!=", self.name),
			},
		)
		if existing:
			frappe.throw(
				frappe._("A price record for {0} on {1} already exists").format(
					self.fuel_type, self.effective_date
				)
			)
