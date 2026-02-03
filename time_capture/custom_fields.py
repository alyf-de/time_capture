from .utils import identity as _


def get_custom_fields():
	return {
		"Attendance": [
			{
				"fieldname": "expected_working_hours",
				"fieldtype": "Float",
				"insert_after": "working_hours",
				"label": _("Expected Working Hours"),
				"fetch_from": "",
				"read_only": 1,
				"default": "0",
				"translatable": 0,
			},
			{
				"label": _("Flexitime"),
				"fieldname": "flexitime",
				"insert_after": "expected_working_hours",
				"fieldtype": "Float",
				"read_only": 1,
				"default": "0",
				"precision": "2",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "custom_absence_plan",
				"fieldtype": "Link",
				"insert_after": "leave_application",
				"label": _("Absence Plan"),
				"no_copy": 1,
				"options": "Absence Plan",
				"read_only": 1,
			},
			{
				"fieldname": "custom_leave_type_absence_plan",
				"fieldtype": "Link",
				"insert_after": "custom_absence_plan",
				"label": _("Leave Type (Absence Plan)"),
				"no_copy": 1,
				"options": "Leave Type",
				"read_only": 1,
			},
			{
				"label": _("Time Capture"),
				"fieldname": "custom_time_capture",
				"insert_after": "attendance_request",
				"fieldtype": "Link",
				"options": "Time Capture",
				"read_only": 1,
				"allow_on_submit": 1,
			},
		],
		"Employee": [
			{
				"fieldname": "custom_no_supervisor_required",
				"fieldtype": "Check",
				"label": _("No Supervisor Required"),
				"insert_after": "reports_to",
				"default": 0,
				"description": _(
					"Should be checked if the employee is a CEO (or has no supervisor for some reason)."
				),
			},
			{
				"fieldname": "expected_working_hours",
				"fieldtype": "Table",
				"insert_after": "attendance_device_id",
				"label": _("Expected Working Hours"),
				"reqd": 1,
				"options": "Employee Expected Working Hours",
				"read_only_depends_on": "eval:!doc.__islocal;",
			},
			{
				"fieldname": "custom_change_expected_hours",
				"fieldtype": "Button",
				"label": _("Change/Add Expected Hours"),
				"insert_after": "expected_working_hours",
				"depends_on": "eval:!doc.__islocal;",
			},
			{
				"label": _("Leave Policy"),
				"fieldname": "leave_policy",
				"insert_after": "holiday_list",
				"fieldtype": "Link",
				"options": "Leave Policy",
				"reqd": 1,
			},
		],
		"Leave Type": [
			{
				"fieldname": "custom_compensatory_off",
				"fieldtype": "Check",
				"insert_after": "is_compensatory",
				"label": _("Compensatory Off"),
				"default": 0,
			},
		],
		"Task": [
			{
				"fieldname": "custom_is_active",
				"label": "Is Active",
				"insert_after": "subject",
				"fieldtype": "Select",
				"options": "Yes\nNo",
				"default": "Yes",
				"translatable": 1,
			},
			{
				"fieldname": "custom_hourly_billed",
				"label": "Hourly Billed",
				"insert_after": "color",
				"fieldtype": "Check",
				"default": "1",
			},
		],
		"Timesheet": [
			{
				"label": _("Time Capture"),
				"fieldname": "custom_time_capture",
				"insert_after": "parent_project",
				"fieldtype": "Link",
				"options": "Time Capture",
				"read_only": 1,
			},
			{
				"label": _("Freelancer Time Capture"),
				"fieldname": "freelancer_time_capture",
				"insert_after": "custom_time_capture",
				"fieldtype": "Link",
				"options": "Freelancer Time Capture",
				"read_only": 1,
			},
			{
				"label": _("Freelancer User"),
				"fieldname": "freelancer_user",
				"insert_after": "employee",
				"fieldtype": "Link",
				"options": "User",
				"read_only": 1,
			},
		],
	}
