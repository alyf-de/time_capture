import frappe

from time_capture.scripts.attendance import _calculate_attendance_metrics


def execute():
	attendances = frappe.get_all("Attendance", filters={"docstatus": 1})
	for attendance in attendances:
		doc = frappe.get_doc("Attendance", attendance.name)
		working_hours, expected_working_hours, flexitime = _calculate_attendance_metrics(doc)
		frappe.db.set_value(
			"Attendance",
			doc.name,
			{
				"working_hours": working_hours,
				"expected_working_hours": expected_working_hours,
				"flexitime": flexitime,
			},
		)
