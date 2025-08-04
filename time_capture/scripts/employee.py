import frappe
from frappe import _
from frappe.utils import getdate
from frappe.utils.data import today
from hrms.hr.utils import get_leave_period


def validate(doc, method=None):
	if doc.is_new():
		create_leave_policy_assignment(doc)
	elif not doc.is_new() and doc.has_value_changed("leave_policy"):
		frappe.msgprint(
			_(
				"Leave Policy has been changed. Note, that this will not update existing Leave Allocations or create/update future Leave Allocations."
			)
		)
		# A new feature is planned, that will regularly create new Leave Allocations for new periods.
		# TODO: Update this message when the feature is implemented.


def before_validate(doc, method):
	validate_expected_working_hours(doc)


def validate_expected_working_hours(doc):
	if not getdate(doc.date_of_joining) == min(getdate(ewh.valid_from) for ewh in doc.expected_working_hours):
		frappe.throw(_("Date of Joining is not the same as the earliest date of Expected Working Hours."))


def create_leave_policy_assignment(doc):
	leave_period = get_leave_period(today(), today(), doc.company)

	leave_policy_assignment = frappe.get_doc(
		{
			"doctype": "Leave Policy Assignment",
			"employee": doc.employee,
			"employee_name": doc.employee_name,
			"leave_policy": doc.leave_policy,
			"leave_period": leave_period[0].name,
			"assignment_based_on": "Leave Period",
			"is_active": 1,
		},
	)
	leave_policy_assignment.insert()
	leave_policy_assignment.submit()


def get_expected_working_hours(employee_id, date):
	"""
	Get the expected working hours for an employee on a specific date.
	"""
	return frappe.db.get_value(
		"Employee Expected Working Hours",
		filters={"parent": employee_id, "valid_from": ("<=", date)},
		fieldname="expected_daily_working_hours",
		order_by="valid_from desc",
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
