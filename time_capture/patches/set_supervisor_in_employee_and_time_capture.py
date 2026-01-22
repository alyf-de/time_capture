import frappe


def execute():
	"""
	Set Reports To in Employee and Time Capture.
	"""
	set_reports_to_in_employee()
	set_reports_to_in_time_capture()


def set_reports_to_in_employee():
	"""
	Set Reports To in Employee.
	"""
	employees = frappe.db.get_all("Employee", fields=["name", "leave_approver"])
	for employee in employees:
		doc = frappe.get_doc("Employee", employee.name)
		if employee.leave_approver:
			supervising_employee = frappe.db.get_all(
				"Employee", filters={"user_id": employee.leave_approver}, pluck="name"
			)
			if supervising_employee:
				doc.reports_to = supervising_employee[0]

		if not doc.reports_to:
			doc.custom_no_supervisor_required = 1

		try:
			doc.save()
		except Exception as e:
			print(f"Error setting Reports To for Employee {employee.name}: {e}")


def set_reports_to_in_time_capture():
	"""
	Set Reports To in Time Capture.
	"""
	for employee in frappe.db.get_all(
		"Employee", filters={"leave_approver": ["is", "set"]}, fields=["name", "leave_approver"]
	):
		frappe.db.set_value(
			"Time Capture", {"employee": employee.name}, "supervisor_email", employee.leave_approver
		)
