import frappe
from erpnext.setup.doctype.employee.employee import is_holiday
from frappe import _
from frappe.utils import getdate
from frappe.utils.data import today
from hrms.hr.utils import get_leave_period

from time_capture.scripts.holiday_list import validate_holiday_list_period_for_employee


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
	if not doc.is_new() and doc.has_value_changed("holiday_list") and doc.holiday_list:
		from_date, to_date = frappe.db.get_value("Holiday List", doc.holiday_list, ["from_date", "to_date"])
		validate_holiday_list_period_for_employee(doc.name, from_date, to_date)


def before_validate(doc, method):
	validate_expected_working_hours(doc)


def validate_expected_working_hours(doc):
	if not getdate(doc.date_of_joining) == min(getdate(ewh.valid_from) for ewh in doc.expected_working_hours):
		frappe.throw(
			_("The date of joining ({0}) has to be the earliest date of Expected Working Hours.").format(
				frappe.utils.format_date(doc.date_of_joining)
			)
		)

	for ewh in doc.expected_working_hours:
		if ewh.expected_daily_working_hours < 0:
			frappe.throw(
				_("Expected Daily Working Hours cannot be less than 0h.").format(
					frappe.utils.format_date(ewh.valid_from)
				)
			)
		if ewh.expected_daily_working_hours > 12:
			frappe.throw(
				_("Expected Daily Working Hours cannot be greater than 12h.").format(
					frappe.utils.format_date(ewh.valid_from)
				)
			)


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

	_show_leave_types_created_info(doc.leave_policy)


def _show_leave_types_created_info(leave_policy):
	"""
	Shows a message indicating the Leave Types included in the Leave Policy
	and the Leave Types that exist, but are not included in the Leave Policy.
	"""
	created_leave_types = frappe.db.get_all(
		"Leave Policy Detail",
		filters={"parent": leave_policy},
		pluck="leave_type",
	)
	all_leave_types = frappe.db.get_all("Leave Type", pluck="name")
	not_created_leave_types = [lt for lt in all_leave_types if lt not in created_leave_types]
	if not_created_leave_types:
		frappe.msgprint(
			_(
				"Note: Following Leaves Types were created: {0}.<br>Following Leave Types were not created: {1}"
			).format(
				", ".join(created_leave_types),
				", ".join(not_created_leave_types),
			)
		)


def get_expected_working_hours(employee_id, date, validate_active_holiday_list=True):
	"""
	Get the expected working hours for an employee on a specific date.
	"""
	date = getdate(date)
	holiday_list = frappe.db.get_value("Employee", employee_id, "holiday_list")
	if validate_active_holiday_list:
		hl_from_date, hl_to_date = frappe.db.get_value("Holiday List", holiday_list, ["from_date", "to_date"])
		if not (hl_from_date <= date <= hl_to_date):
			frappe.throw(
				_(
					"The date {0} is not within the period of the active holiday list for employee {1}."
				).format(frappe.utils.format_date(date), employee_id)
			)

	if holiday_list and is_holiday(employee=employee_id, date=date):
		return 0.0

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
def save_expected_working_hours_and_update_attendances(employee_id, expected_working_hours):
	"""
	Save expected working hours to employee and update all attendances.
	"""
	frappe.has_permission(doctype="Employee", doc=employee_id, ptype="write", throw=True)

	# Load doc and clear existing expected working hours
	employee = frappe.get_doc("Employee", employee_id)
	employee.expected_working_hours = []

	# turn expected_working_hours from string to a list of dicts
	expected_working_hours = frappe.parse_json(expected_working_hours)

	# Add new expected working hours
	for ewh_data in expected_working_hours:
		employee.append(
			"expected_working_hours",
			{
				"valid_from": ewh_data.get("valid_from"),
				"expected_daily_working_hours": ewh_data.get("expected_daily_working_hours"),
			},
		)

	# Save employee document (this will trigger validation) and update attendances
	employee.save()
	update_attendances_for_employee(employee_id)


def update_attendances_for_employee(employee_id, get_working_hours=False):
	"""
	Update all attendances for an employee by recalculating the attendance metrics.

	:param employee_id: The Employee ID whose submitted Attendance records should be updated.
	:param get_working_hours: If True, forces recalculation of working hours for each
		Attendance record (via :func:`get_attendance_metrics`), using the latest underlying
		source data. Leave as False (the default) when only status or expected working hours
		need to be refreshed and no change to the way working hours are derived is required.
		Set this to True when working-hours-related inputs (such as shifts, logs, or
		configuration affecting working hours) have changed and working hours must be
		recomputed.
	"""
	from time_capture.scripts.attendance import get_attendance_metrics

	attendances_to_update = frappe.get_all(
		"Attendance",
		filters={"employee": employee_id, "docstatus": 1},
		pluck="name",
	)
	for attendance_id in attendances_to_update:
		doc = frappe.get_doc("Attendance", attendance_id)
		status, working_hours, expected_working_hours, flexitime = get_attendance_metrics(
			doc, get_working_hours
		)
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
	frappe.msgprint(_("{0} Attendances updated successfully.").format(len(attendances_to_update)))
