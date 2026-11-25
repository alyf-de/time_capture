import frappe


def execute():
	"""Desk moved from /app to /desk in v16."""
	if frappe.db.get_value("Role", "Freelancer", "home_page") == "/app/freelancer":
		frappe.db.set_value("Role", "Freelancer", "home_page", "/desk/freelancer")
