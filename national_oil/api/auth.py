import frappe
from frappe.auth import LoginManager

@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_csrf_token():
	"""
	Public endpoint to get CSRF token for unauthenticated users.
	Used by SPA frontend before login.
	"""
	return {
		'csrf_token': frappe.session.data.get('csrf_token', ''),
		'sid': frappe.session.sid
	}

@frappe.whitelist(allow_guest=True, methods=["POST"])
def login(usr: str, pwd: str):
	"""
	Custom login endpoint for SPA login.
	CSRF validation is disabled at site level for development.
	"""
	try:
		login_manager = LoginManager()
		login_manager.authenticate(user=usr, pwd=pwd)
		login_manager.post_login()
		
		# Return user object (Frappe will wrap in 'message' key)
		user = frappe.get_doc('User', frappe.session.user)
		return {
			'name': user.name,
			'email': user.email,
			'full_name': user.full_name,
		}
	except frappe.AuthenticationError as e:
		frappe.throw(str(e), frappe.AuthenticationError)
	except Exception as e:
		frappe.throw(f"Login failed: {str(e)}", frappe.ValidationError)

@frappe.whitelist()
def get_petrol_user_context():
	"""
	Return petrol-specific user context for authenticated users.
	For ERPNext users: Returns basic user info + petrol role status
	For petrol users: Returns petrol user details + permissions
	"""
	if frappe.session.user == "Guest":
		frappe.throw("Not authenticated", frappe.PermissionError)
	
	user_doc = frappe.get_doc('User', frappe.session.user)
	user_roles = [role.role for role in user_doc.roles]
	
	return {
		'user': frappe.session.user,
		'email': user_doc.email,
		'full_name': user_doc.full_name,
		'roles': user_roles,
		'has_petrol_access': 'Petrol Manager' in user_roles or 'System Manager' in user_roles,
	}

