import frappe

from time_capture.scripts.employee import update_attendances_for_employee


def execute():
	employees = frappe.get_all("Employee", filters={"status": "Active"})
	for employee in employees:
		update_attendances_for_employee(employee.name)
