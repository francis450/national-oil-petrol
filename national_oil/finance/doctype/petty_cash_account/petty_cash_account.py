import frappe
from frappe.model.document import Document


class PettyCashAccount(Document):
	def replenish(self, amount):
		"""Add funds to the account balance."""
		self.balance = (self.balance or 0) + amount
		self.last_replenished = frappe.utils.today()
		self.save()
