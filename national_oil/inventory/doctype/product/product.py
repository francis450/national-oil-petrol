import frappe
from frappe.model.document import Document


class Product(Document):
	def validate(self):
		if self.is_fuel and not self.fuel_type:
			frappe.throw(frappe._("Fuel Type is required for fuel products"))
