import frappe

def get_context(context):
	"""
	Serve the National Oil Petrol SPA at /app/petrol route without Frappe website wrapper.
	Enables automatic session sharing with ERPNext.
	"""
	context.no_cache = 1
	context.no_breadcrumbs = True
	
	# Tell Frappe to skip the standard website template
	frappe.response['type'] = 'page'
	
	return context
