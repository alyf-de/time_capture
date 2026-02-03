import frappe
from frappe import _
from frappe.utils import getdate

from time_capture.scripts.employee import get_expected_working_hours
from time_capture.time_capture.doctype.time_capture.time_capture import _create_time_capture


def on_change(doc, event):
	set_attendance_metrics(doc)
	if (
		(doc.leave_type or doc.custom_leave_type_absence_plan)
		and frappe.utils.getdate(doc.attendance_date) <= frappe.utils.getdate()
		and doc.docstatus != 2
	):
		delete_time_capture(doc)


def on_cancel(doc, event):
	employee = frappe.get_doc("Employee", doc.employee)
	_create_time_capture(employee, doc.attendance_date)


def set_attendance_metrics(doc):
	status, working_hours, expected_working_hours, flexitime = get_attendance_metrics(doc)
	if doc.docstatus == 1:
		# This is needed if a late Time Capture is submitted and updates the Attendance metrics.
		frappe.db.set_value(
			"Attendance",
			doc.name,
			{
				"status": status,
				"working_hours": working_hours,
				"expected_working_hours": expected_working_hours,
				"flexitime": flexitime,
			},
		)
	else:
		# This is the normal flow.
		doc.status = status
		doc.working_hours = working_hours
		doc.expected_working_hours = expected_working_hours
		doc.flexitime = flexitime


def get_attendance_metrics(doc, get_working_hours=False):
	"""
	Calculates actual working hours, expected working hours, and flexitime
	based on the attendance document. Also sets the attendance status.
	Args:
	                                doc (frappe.model.document.Document): The attendance document.
	Returns:
	                                tuple: (status, actual_working_hours, expected_working_hours, flexitime)
	"""
	leave_type = doc.leave_type or doc.custom_leave_type_absence_plan
	if leave_type and leave_type == frappe.db.get_single_value("Time Capture Settings", "sick_leave_type"):
		# Special Case: Sick Leaves are not considered for working hours or expected working hours.
		return "On Leave", 0.0, 0.0, 0.0

	expected_working_hours_full_day = get_expected_working_hours(doc.employee, doc.attendance_date) or 0.0
	is_half_day = _get_is_half_day(doc.attendance_date, doc.leave_application)

	# 1: Get Working Hours
	if get_working_hours and doc.custom_time_capture:
		working_hours = frappe.db.get_value("Time Capture", doc.custom_time_capture, "working_time") or 0.0
		if working_hours > 0:
			working_hours = working_hours / 3600
	else:
		working_hours = doc.working_hours or 0.0

	# 2: Get Status
	status = _get_attendance_status(is_half_day, expected_working_hours_full_day, working_hours, leave_type)

	# 3: Get Expected Working Hours
	if leave_type:
		expected_working_hours = _get_expected_working_hours_for_leave_days(
			expected_working_hours_full_day, leave_type, is_half_day
		)
	else:
		expected_working_hours = expected_working_hours_full_day

	flexitime = working_hours - expected_working_hours
	return status, working_hours, expected_working_hours, flexitime


def _get_attendance_status(
	is_half_day: bool, expected_working_hours_full_day: float, working_hours: float, leave_type: str | None
):
	if leave_type and not is_half_day:
		return "On Leave"

	if working_hours == 0:
		return "Absent"

	if is_half_day:
		return "Half Day"

	return "Present"


def _get_is_half_day(date: str, leave_application: str | None):
	"""
	Return a boolean indicating if the leave application date is a half day.
	"""
	if not leave_application:
		return False
	has_half_day, half_day_date = frappe.db.get_value(
		"Leave Application", leave_application, ["half_day", "half_day_date"]
	)
	if not has_half_day or not half_day_date:
		return False
	return getdate(half_day_date) == getdate(date)


def _get_expected_working_hours_for_leave_days(
	expected_working_hours_full_day: float, leave_type: str, is_half_day: bool
):
	"""
	Return the expected working hours for a Leave Day considering Half Days and Overtime Reduction.
	"""
	if expected_working_hours_full_day == 0:
		# This should never happen, but just to avoid division by zero.
		return 0.0
	if frappe.db.get_value("Leave Type", leave_type, "is_compensatory"):
		# No matter if a compensatory leave is full or half day the expected hours will be a full day.
		return expected_working_hours_full_day
	if is_half_day:
		return expected_working_hours_full_day / 2
	return 0.0


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
		frappe.delete_doc("Time Capture", time_capture[0].name, ignore_permissions=True)
		# Ignores permissions, because Leave Approver doesn't necessarily have permission to delete Time Captures.
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


def create_absent_attendance_for_draft_time_captures():
	"""
	Create Absent Attendances for Time Captures that are in draft state and have a date in the past.
	"""
	time_captures = frappe.db.get_all(
		"Time Capture",
		filters={"docstatus": 0, "date": ("<", frappe.utils.nowdate())},
		fields=["employee", "date", "name"],
	)
	for time_capture in time_captures:
		try:
			if not frappe.db.exists(
				"Attendance",
				{
					"docstatus": ("!=", 2),
					"employee": time_capture.employee,
					"attendance_date": time_capture.date,
				},
			):
				frappe.get_doc(
					{
						"doctype": "Attendance",
						"employee": time_capture.employee,
						"attendance_date": time_capture.date,
						"custom_time_capture": time_capture.name,
						"status": "Absent",
						"working_hours": 0,
					}
				).insert().submit()
		except Exception:
			frappe.log_error(
				title=_("Error creating Attendance"),
				message=frappe.get_traceback(),
				reference_doctype="Time Capture",
				reference_name=time_capture.name,
			)
