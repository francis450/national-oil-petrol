import frappe
from frappe.model.document import Document


class MPesaSettings(Document):
	@property
	def api_base_url(self):
		if self.environment == "Production":
			return "https://api.safaricom.co.ke"
		return "https://sandbox.safaricom.co.ke"
