import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PerformanceReview(Document):
	def validate(self):
		self.deviation = flt(self.hit_amount) - flt(self.target_amount)
		if flt(self.target_amount):
			self.variance_percent = (self.deviation / flt(self.target_amount)) * 100
