import frappe


def execute():
	"""Migrate is_compensatory to custom_compensatory_off, then clear is_compensatory."""
	if not frappe.db.has_column("Leave Type", "is_compensatory"):
		return
	if not frappe.db.has_column("Leave Type", "custom_compensatory_off"):
		return

	frappe.db.set_value(
		"Leave Type",
		{"is_compensatory": 1},
		{"custom_compensatory_off": 1, "is_compensatory": 0},
	)
