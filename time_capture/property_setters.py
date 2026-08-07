from .utils import identity as _


def get_property_setters():
	return [
		("Attendance", "status", "allow_on_submit", "1"),
		("Attendance", "working_hours", "allow_on_submit", "1"),
		("Attendance", "working_hours", "precision", "2"),
		("Employee", "reports_to", "mandatory_depends_on", "eval:!doc.custom_no_supervisor_required"),
		("Employee", "reports_to", "read_only_depends_on", "eval: doc.custom_no_supervisor_required"),
		("Employee", "expense_approver", "read_only", "0"),
		("Employee", "expense_approver", "description", _("Fetched from <i>Reports To</i> field, if empty.")),
		("Employee", "leave_approver", "read_only", "0"),
		("Employee", "expense_approver", "no_copy", "1"),
		("Employee", "leave_approver", "description", _("Fetched from <i>Reports To</i> field, if empty.")),
		("Employee", "leave_approver", "no_copy", "1"),
		("Employee", "shift_request_approver", "read_only", "0"),
		(
			"Employee",
			"shift_request_approver",
			"description",
			_("Fetched from <i>Reports To</i> field, if empty."),
		),
		("Employee", "shift_request_approver", "no_copy", "1"),
		("Employee", "working_hours_per_week", "hidden", "1"),
		("Employee", "holiday_list", "reqd", "0"),
		("Employee", "holiday_list", "mandatory_depends_on", "eval:doc.status == 'Active'"),
		("Leave Type", "is_compensatory", "hidden", "1"),
	]
