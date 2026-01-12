import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method=None):
	if not doc.is_new() and (doc.has_value_changed("from_date") or doc.has_value_changed("to_date")):
		validate_period(doc.name, doc.from_date, doc.to_date)


def validate_period(holiday_list: str, from_date: str, to_date: str):
	"""Validate Holiday List period for all Employees."""
	employees = frappe.db.get_all("Employee", filters={"holiday_list": holiday_list}, pluck="name")
	for employee in employees:
		validate_holiday_list_period_for_employee(employee, from_date, to_date)


def validate_holiday_list_period_for_employee(employee: str, from_date: str, to_date: str):
	"""Validate that all attendances for an employee are within the holiday list period."""
	from_date = getdate(from_date)
	to_date = getdate(to_date)

	filters = {"employee": employee, "docstatus": 1}

	if not frappe.db.exists("Attendance", filters):
		return

	attendance_span = frappe.db.get_all(
		"Attendance",
		filters=filters,
		fields=[
			"MIN(attendance_date) as min_attendance_date",
			"MAX(attendance_date) as max_attendance_date	",
		],
	)
	min_attendance_date = attendance_span[0].min_attendance_date
	max_attendance_date = attendance_span[0].max_attendance_date

	if from_date <= min_attendance_date and to_date >= max_attendance_date:
		# All Attendances are within the Holiday List period.
		return

	msg = _("Employee {0} has Attendances outside the Holiday List period.").format(employee)
	msg += "<br>" + _(
		"Please adjust the Holiday List, such that it covers all Attendances (from {0} to {1} and possibly ongoing)."
	).format(frappe.utils.format_date(min_attendance_date), frappe.utils.format_date(max_attendance_date))
	frappe.throw(msg)
