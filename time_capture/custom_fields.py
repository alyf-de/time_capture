
custom_fields = {
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

not_sure_if_needed = {
	"Task": [
		{
			"fieldname": "naming_series",
			"label": "Naming Series",
			"insert_after": "column_break0",
			"fieldtype": "Select",
			"reqd": 0,
			"hidden": 1,
			"depends_on": "eval: doc.__islocal",
		},
		{
			"fieldname": "custom_is_active",
			"label": "Is Active",
			"insert_after": "subject",
			"fieldtype": "Select",
			"options": "Yes\nNo",
			"default": "No",
			"translatable": 1,
		},
		{
			"fieldname": "custom_project_manager",
			"label": "Project Manager",
			"insert_after": "project",
			"fieldtype": "Link",
			"options": "User",
			"fetch_from": "project.custom_project_manager",
			"read_only": 1,
		},
		{
			"fieldname": "custom_hourly_billed",
			"label": "Hourly Billed",
			"insert_after": "color",
			"fieldtype": "Check",
			"default": "1",
			"depends_on": "eval: !doc.__islocal",
		},
	],
}
