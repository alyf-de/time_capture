import frappe
from frappe import _

from time_capture.time_capture.doctype.time_capture.time_capture import _create_time_capture


def on_change(doc, event):
	if not doc.flags.flexitime_updated:
		set_flexitime_and_working_time(doc)


def on_submit(doc, event):
	if doc.leave_type and doc.attendance_date <= frappe.utils.nowdate():
		delete_time_capture(doc)


def on_cancel(doc, event):
	employee = frappe.get_doc("Employee", doc.employee)
	_create_time_capture(employee, doc.attendance_date)


def set_flexitime_and_working_time(doc):
	doc.flags.flexitime_updated = True
	expected_working_hours = frappe.db.get_value("Employee", doc.employee, "expected_daily_working_hours")
	working_hours = doc.working_hours
	if not doc.leave_type:
		if expected_working_hours:
			HALF_DAY = expected_working_hours / 2
			OVERTIME_FACTOR = 1.15
			MAX_HALF_DAY = HALF_DAY * OVERTIME_FACTOR * 60 * 60
		doc.db_set({"status": "Present" if working_hours > MAX_HALF_DAY else "Half Day"})
	else:
		if frappe.db.get_value("Leave Type", doc.leave_type, "is_compensatory") == 1:
			working_hours = 0
		else:
			expected_working_hours = 0
			working_hours = 0
	doc.db_set(
		{
			"expected_working_hours": expected_working_hours,
			"working_hours": working_hours,
			"flexitime": working_hours - expected_working_hours,
		}
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
