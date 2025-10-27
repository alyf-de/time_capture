import frappe

from time_capture.scripts.attendance import delete_time_capture


def execute():
	"""
	Deletes Time Captures that are not needed anymore.
	Reason: They have been outdated by leave days.
	"""
	leave_days = frappe.db.get_all(
		"Attendance",
		filters={
			"docstatus": 1,
			"custom_time_capture": ["!=", None],
			"leave_type": ["!=", None],
			"attendance_date": ("<=", frappe.utils.nowdate()),
		},
		pluck="name",
	)
	for attendance_name in leave_days:
		delete_time_capture(frappe.get_doc("Attendance", attendance_name))
