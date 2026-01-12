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

	min_attendance_date = frappe.db.get_all(
		"Attendance", filters=filters, order_by="attendance_date asc", limit=1, pluck="attendance_date"
	)[0]
	max_attendance_date = frappe.db.get_all(
		"Attendance", filters=filters, order_by="attendance_date desc", limit=1, pluck="attendance_date"
	)[0]

	if min_attendance_date <= from_date or max_attendance_date >= to_date:
		msg = _("Employee {0} has Attendances outside the Holiday List period.").format(employee)
		msg += "<br>" + _(
			"Please adjust the Holiday List, such that it covers all Attendances (from {0} to {1} and possibly ongoing)."
		).format(frappe.utils.format_date(min_attendance_date), frappe.utils.format_date(max_attendance_date))
		frappe.throw(msg)
