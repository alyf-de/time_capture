from .utils import identity as _


def get_custom_fields():
	return {
		"Attendance": [
			{
				"fieldname": "expected_working_hours",
				"fieldtype": "Float",
				"insert_after": "working_hours",
				"label": "Expected Working Hours",
				"read_only": 1,
				"default": "0",
				"translatable": 0,
			},
			{
				"label": "Flexitime",
				"fieldname": "flexitime",
				"insert_after": "expected_working_hours",
				"fieldtype": "Float",
				"read_only": 1,
				"default": "0",
			},
			{
				"label": "Time Capture",
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
				"label": "Expected Daily Working Hours",
				"translatable": 0,
			},
		],
		"Timesheet": [
			{
				"label": "Time Capture",
				"fieldname": "custom_time_capture",
				"insert_after": "parent_project",
				"fieldtype": "Link",
				"options": "Time Capture",
				"read_only": 1,
			},
		],
	}
