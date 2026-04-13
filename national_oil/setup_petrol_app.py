"""
National Oil Petrol app setup.
Creates Petrol Manager role and module workspace.
"""
import frappe


def setup_petrol_app():
	"""Set up National Oil Petrol app components"""
	
	print("Setting up National Oil Petrol app...")
	
	# 1. Create Petrol Manager Role
	create_petrol_manager_role()
	
	# 2. Create National Oil Petrol Module
	create_national_oil_module()
	
	# 3. Create Petrol Page (for /app/petrol route)
	create_petrol_page()
	
	# 4. Create Workspace
	create_petrol_workspace()
	
	print("✓ National Oil Petrol app setup complete!")
	

def create_petrol_manager_role():
	"""Create Petrol Manager role with appropriate permissions"""
	print("\n→ Creating Petrol Manager role...")
	
	role_name = "Petrol Manager"
	
	# Check if role exists
	if frappe.db.exists("Role", role_name):
		print(f"  ✓ Role '{role_name}' already exists")
		return
	
	# Create role
	role = frappe.new_doc("Role")
	role.role_name = role_name
	role.insert(ignore_permissions=True)
	frappe.db.commit()
	
	print(f"  ✓ Created role: {role_name}")


def create_national_oil_module():
	"""Create National Oil Petrol module in ERPNext"""
	print("\n→ Creating National Oil Petrol module...")
	
	module_name = "National Oil Petrol"
	
	if frappe.db.exists("Module Def", module_name):
		print(f"  ✓ Module '{module_name}' already exists")
		return
	
	module = frappe.new_doc("Module Def")
	module.module_name = module_name
	module.app_name = "national_oil"
	module.insert(ignore_permissions=True)
	frappe.db.commit()
	
	print(f"  ✓ Created module: {module_name}")


def create_petrol_page():
	"""Create Petrol page for /app/petrol route"""
	print("\n→ Creating Petrol page for /app/petrol route...")
	
	page_name = "Petrol"
	
	if frappe.db.exists("Page", page_name):
		print(f"  ✓ Page '{page_name}' already exists")
		return
	
	try:
		page = frappe.new_doc("Page")
		page.page_name = page_name
		page.title = "National Oil Petrol Dashboard"
		page.module = "National Oil Petrol"
		page.insert(ignore_permissions=True)
		frappe.db.commit()
		
		print(f"  ✓ Created page: {page_name} (accessible at /app/petrol)")
	except Exception as e:
		print(f"  ⚠ Page creation note: {str(e)[:100]}")
		print(f"    Petrol is still accessible at: /petrol")


def create_petrol_workspace():
	"""Create Petrol Workspace with dashboard link"""
	print("\n→ Creating Petrol Workspace...")
	
	workspace_name = "National Oil Petrol"
	
	if frappe.db.exists("Workspace", workspace_name):
		print(f"  ✓ Workspace '{workspace_name}' already exists")
		return
	
	try:
		workspace = frappe.new_doc("Workspace")
		workspace.workspace_name = workspace_name
		workspace.module = "National Oil Petrol"
		workspace.icon = "icon-building"
		workspace.label = "Petrol Dashboard"
		workspace.insert(ignore_permissions=True)
		frappe.db.commit()
		
		print(f"  ✓ Created workspace: {workspace_name}")
	except Exception as e:
		print(f"  ⚠ Workspace creation note: {str(e)[:100]}")
		print(f"    (Create workspace manually via desk if needed)")


# Make functions callable for bench execute
__all__ = ['setup_petrol_app', 'create_petrol_manager_role', 'create_national_oil_module', 'create_petrol_page', 'create_petrol_workspace']

