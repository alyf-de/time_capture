import frappe


def execute():
	if not frappe.db.exists(
		"Custom Field", {"dt": "Employee", "fieldname": "expected_daily_working_hours", "fieldtype": "Float"}
	):
		return
	for e in frappe.db.get_all("Employee", filters={"expected_daily_working_hours": ["is", "set"]}):
		print(f"Updating {e.name}")
		employee = frappe.get_doc("Employee", e.name)
		employee.append(
			"expected_working_hours",
			{
				"valid_from": employee.date_of_joining,
				"expected_daily_working_hours": employee.expected_daily_working_hours,
			},
		)
		employee.save()
	frappe.db.delete(
		"Custom Field", {"dt": "Employee", "fieldname": "expected_daily_working_hours", "fieldtype": "Float"}
	)
