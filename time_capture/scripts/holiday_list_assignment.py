import frappe
from frappe import _

from time_capture.scripts.employee import recalculate_attendances
from time_capture.scripts.holiday_list import (
	get_holiday_list_periods,
	validate_holiday_list_periods_for_employee,
)


def on_submit(doc, method=None):
	employees = get_affected_employees(doc)
	validate_attendance_coverage(doc, employees)
	update_attendances(doc, employees)


def get_affected_employees(doc) -> list[str]:
	"""Return the Employees a Holiday List Assignment applies to."""
	if doc.applicable_for == "Employee":
		return [doc.assigned_to]

	return frappe.get_all("Employee", filters={"company": doc.assigned_to}, pluck="name")


def validate_attendance_coverage(doc, employees: list[str]):
	"""Validate that the Holiday List covers all Attendances the assignment applies to."""
	for employee in employees:
		validate_holiday_list_periods_for_employee(employee, assignment=doc.name)


def update_attendances(doc, employees: list[str]):
	"""Recalculate expected working hours and flexitime of the Attendances in the assignment's period."""
	updated = 0
	for employee in employees:
		period = next((p for p in get_holiday_list_periods(employee) if p.name == doc.name), None)
		if period:
			updated += recalculate_attendances(employee, from_date=period.from_date, to_date=period.to_date)

	if updated:
		frappe.msgprint(_("{0} Attendances updated successfully.").format(updated), alert=True)
