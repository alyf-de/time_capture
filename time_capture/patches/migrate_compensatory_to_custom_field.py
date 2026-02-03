import frappe


def execute():
	"""Migrate is_compensatory to custom_compensatory_off, then clear is_compensatory."""
	leave_types = frappe.get_all("Leave Type", filters={"is_compensatory": 1}, pluck="name")
	for leave_type in leave_types:
		frappe.db.set_value("Leave Type", leave_type, {"custom_compensatory_off": 1, "is_compensatory": 0})
