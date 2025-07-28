import frappe
from frappe import _
from frappe.utils import getdate


def before_validate(doc, method):
	validate_expected_working_hours(doc)


def validate_expected_working_hours(doc):
	if not getdate(doc.date_of_joining) == min(getdate(ewh.valid_from) for ewh in doc.expected_working_hours):
		frappe.throw(_("Date of Joining is not the same as the earliest date of Expected Working Hours."))


def get_expected_working_hours(employee_id, date):
	"""
	Get the expected working hours for an employee on a specific date.
	"""
	return (
		frappe.db.get_value(
			"Employee Expected Working Hours",
			filters={"parent": employee_id, "valid_from": ("<=", date)},
			fieldname="expected_daily_working_hours",
			order_by="valid_from desc",
		)
		or 0
	)


@frappe.whitelist()
def update_attendances_with_expected_working_hours(employee_id):
	from time_capture.scripts.attendance import _calculate_attendance_metrics

	if "System Manager" not in frappe.get_roles():
		frappe.throw(_("Only System Manager are allowed to update Attendances with Expected Working Hours."))

	attendances_to_update = frappe.get_all(
		"Attendance",
		filters={"employee": employee_id, "docstatus": 1},
		pluck="name",
	)
	for attendance_id in attendances_to_update:
		doc = frappe.get_doc("Attendance", attendance_id)
		working_hours, expected_working_hours, flexitime = _calculate_attendance_metrics(
			doc, update_from_employee=True
		)
		frappe.db.set_value(
			"Attendance",
			doc.name,
			{
				"working_hours": working_hours,
				"expected_working_hours": expected_working_hours,
				"flexitime": flexitime,
			},
		)
	frappe.msgprint(_("{0} Attendances updated successfully.").format(len(attendances_to_update)))
