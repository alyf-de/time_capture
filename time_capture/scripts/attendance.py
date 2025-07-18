import frappe
from frappe import _

from time_capture.scripts.employee import get_expected_working_hours
from time_capture.time_capture.doctype.time_capture.time_capture import _create_time_capture


def before_insert(doc, event):
	set_attendance_metrics(doc)


def on_submit(doc, event):
	if doc.leave_type and doc.attendance_date <= frappe.utils.nowdate():
		delete_time_capture(doc)


def on_cancel(doc, event):
	employee = frappe.get_doc("Employee", doc.employee)
	_create_time_capture(employee, doc.attendance_date)


def set_attendance_metrics(doc):
	working_hours, expected_working_hours, flexitime = _calculate_attendance_metrics(doc)
	doc.working_hours = working_hours or 0
	doc.expected_working_hours = expected_working_hours or 0
	doc.flexitime = flexitime or 0


def _calculate_attendance_metrics(doc, update_from_employee: bool = False):
	"""
	Calculates actual working hours, expected working hours, and flexitime
	based on the attendance document. Also sets the attendance status.
	Args:
	        doc (frappe.model.document.Document): The attendance document.
	Returns:
	        tuple: (actual_working_hours, expected_working_hours, flexitime)
	"""
	expected_working_hours_full_day = get_expected_working_hours(doc.employee, doc.attendance_date)

	# Handle Leaves
	if doc.leave_type:
		if frappe.db.get_value("Leave Type", doc.leave_type, "is_compensatory"):
			return 0.0, 0.0, -expected_working_hours_full_day
		else:
			return 0.0, 0.0, 0.0

	if expected_working_hours_full_day and not update_from_employee:
		HALF_DAY = expected_working_hours_full_day / 2
		OVERTIME_FACTOR = 1.15
		MAX_HALF_DAY = HALF_DAY * OVERTIME_FACTOR * 60 * 60
		doc.status = "Present" if doc.working_hours > MAX_HALF_DAY else "Half Day"

	# Normal Working Day
	return (
		doc.working_hours,
		expected_working_hours_full_day,
		doc.working_hours - expected_working_hours_full_day,
	)


def delete_time_capture(doc):
	"""
	Deletes untouched Time Captures for days on leave.
	"""
	time_capture = frappe.db.get_all(
		"Time Capture",
		filters={
			"employee": doc.employee,
			"date": doc.attendance_date,
			"docstatus": 0,
			"working_time": 0,
		},
	)
	if time_capture:
		frappe.delete_doc("Time Capture", time_capture[0].name)
	else:
		message = "Keine löschbare Zeitfassung für Mitarbeiter {} am {} gefunden".format(
			doc.employee_name, doc.attendance_date
		)
		message += "<br><br>Mögliche Ursachen: Zeiterfassung wurde von einem System Manager gelöscht oder Mitarbeiter hat die Zeiterfassung bereits bearbeitet."
		frappe.log_error(
			title=_("Time Capture Not Found"),
			message=message,
			reference_doctype=doc.doctype,
			reference_name=doc.name,
		)
