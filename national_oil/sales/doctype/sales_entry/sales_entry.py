import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SalesEntry(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(frappe._("Amount must be greater than zero"))
		if self.payment_method == "Credit" and not self.customer:
			frappe.throw(frappe._("Customer is required for credit sales"))
		self.calculate_variance_from_pump_reading()

	def calculate_variance_from_pump_reading(self):
		if not self.shift:
			self.variance_from_pump_reading = None
			return

		total_expected_sales = frappe.db.get_value("Shift Assignment", self.shift, "total_expected_sales")
		self.variance_from_pump_reading = flt(self.amount) - flt(total_expected_sales)
