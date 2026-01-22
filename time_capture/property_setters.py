def get_property_setters():
	return [
		("Attendance", "status", "allow_on_submit", "1"),
		("Attendance", "working_hours", "allow_on_submit", "1"),
		("Attendance", "working_hours", "precision", "2"),
		("Employee", "reports_to", "mandatory_depends_on", "eval:!doc.custom_no_supervisor_required"),
		("Employee", "expense_approver", "read_only", "1"),
		("Employee", "expense_approver", "description", "Fetched from <i>Reports To</i> field."),
		("Employee", "leave_approver", "read_only", "1"),
		("Employee", "leave_approver", "description", "Fetched from <i>Reports To</i> field."),
		("Employee", "shift_request_approver", "read_only", "1"),
		("Employee", "shift_request_approver", "description", "Fetched from <i>Reports To</i> field."),
		("Employee", "working_hours_per_week", "hidden", "1"),
		("Employee", "holiday_list", "reqd", "1"),
	]
