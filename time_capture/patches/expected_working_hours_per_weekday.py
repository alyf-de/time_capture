import frappe


def execute():
	"""
	This patch moves the expected working hours from a single field to fields per weekday.
	This assumes, that the expected working hours counted from Monday to Friday.
	"""
	for expected_working_hours in frappe.get_all("Employee Expected Working Hours", fields=["*"]):
		for field in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
			frappe.db.set_value(
				"Employee Expected Working Hours",
				expected_working_hours.name,
				field,
				expected_working_hours.expected_daily_working_hours,
			)
