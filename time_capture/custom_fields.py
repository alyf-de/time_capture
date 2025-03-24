from .utils import identity as _


def get_custom_fields():
	return {
		"Attendance": [
			{
				"fieldname": "expected_working_hours",
				"fieldtype": "Float",
				"insert_after": "working_hours",
				"label": _("Expected Working Hours"),
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
			},
			{
				"label": _("Time Capture"),
				"fieldname": "custom_time_capture",
				"insert_after": "attendance_request",
				"fieldtype": "Link",
				"options": "Time Capture",
				"read_only": 1,
			},
		],
		"Employee": [
			{
				"fieldname": "expected_daily_working_hours",
				"fieldtype": "Float",
				"insert_after": "attendance_device_id",
				"label": _("Expected Daily Working Hours"),
				"translatable": 0,
				"reqd": 1,
			},
		],
		"Task": [
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
		],
	}
