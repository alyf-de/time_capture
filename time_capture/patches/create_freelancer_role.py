import frappe


def execute():
	if frappe.db.exists("Role", "Freelancer"):
		print("Role 'Freelancer' already exists, skipping creation. Please, adjust the roles + permissions manually if needed.")
		return
	new_role_doc = frappe.new_doc("Role")
	new_role_doc.role_name = "Freelancer"
	new_role_doc.home_page = "/app/freelancer"
	new_role_doc.save()
