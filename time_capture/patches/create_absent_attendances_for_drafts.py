import frappe


def execute():
	past_draft_time_captures = frappe.db.get_all(
		"Time Capture",
		filters={"docstatus": 0, "date": ("<", frappe.utils.nowdate())},
		fields=["employee", "date", "name"],
	)
	for time_capture in past_draft_time_captures:
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
