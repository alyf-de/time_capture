import frappe


def execute():
	custom_field_filters = {
		"dt": "Employee",
		"fieldname": "expected_daily_working_hours",
		"fieldtype": "Float",
	}
	if not frappe.db.exists("Custom Field", custom_field_filters):
		return

	for employee_id in frappe.get_all(
		"Employee", filters={"expected_daily_working_hours": ("is", "set")}, pluck="name"
	):
		print(f"Updating {employee_id}")

		employee = frappe.get_doc("Employee", employee_id)
		if employee.expected_working_hours or not employee.expected_daily_working_hours:
			continue

		employee.append(
			"expected_working_hours",
			{
				"valid_from": employee.date_of_joining,
				"expected_daily_working_hours": employee.expected_daily_working_hours,
			},
		)
		employee.save()
	frappe.db.delete("Custom Field", custom_field_filters)
