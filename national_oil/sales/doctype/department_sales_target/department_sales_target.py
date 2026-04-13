import frappe
from frappe.model.document import Document
from frappe.utils import flt


class DepartmentSalesTarget(Document):
	def validate(self):
		if flt(self.target_amount) <= 0:
			frappe.throw(frappe._("Target Amount must be greater than zero"))

	def recalculate(self):
		"""Recalculate hit_amount and deviation from submitted Sales Entries."""
		filters = [
			["Sales Entry", "department", "=", self.department],
			["Sales Entry", "dated", ">=", self.period_start],
			["Sales Entry", "docstatus", "=", 1],
		]
		if self.period_end:
			filters.append(["Sales Entry", "dated", "<=", self.period_end])

		result = frappe.db.get_value(
			"Sales Entry",
			filters,
			"sum(amount)",
			as_dict=False,
		)
		self.hit_amount = flt(result)
		self.deviation = self.hit_amount - flt(self.target_amount)
		if flt(self.target_amount):
			self.variance_percent = (self.deviation / flt(self.target_amount)) * 100
		self.save()
