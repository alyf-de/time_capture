import frappe
from frappe import _


@frappe.whitelist()
def get_working_time_summary_for_employee(employee: str, beautified: bool = True) -> dict:
	frappe.has_permission("Employee", doc=employee, throw=True)

	flexitime_correction = _get_last_flexitime_correction(employee)
	attendance_sum = _get_flexitime_sum_from_attendance(
		employee, flexitime_correction.get("date"), frappe.utils.getdate()
	)
	current_balance = (flexitime_correction.get("flexitime_hours") or 0) + (attendance_sum or 0)
	future_balance_changes = _get_flexitime_sum_from_attendance(employee, frappe.utils.getdate())
	# these changes are mainly expected through planned overtime reductions
	future_balance = current_balance + future_balance_changes
	open_time_captures = len(
		frappe.db.get_all(
			"Time Capture",
			filters={"employee": employee, "docstatus": 0},
		)
	)

	summary = {
		"flexitime_correction": flexitime_correction,
		"current_balance": current_balance,
		"future_balance_changes": future_balance_changes,
		"future_balance": future_balance,
		"open_time_captures": open_time_captures,
	}
	return beautify_report_data(summary) if beautified else summary


def _get_last_flexitime_correction(employee: str) -> float:
	""" """
	flexitime_correction = frappe.db.get_value(
		"Flexitime Correction",
		filters={
			"employee": employee,
			"docstatus": 1,
			"date": ("<=", frappe.utils.getdate()),
		},
		fieldname=["flexitime_hours", "date"],
		order_by="date DESC",
		as_dict=True,
	)
	return flexitime_correction or {"flexitime_hours": 0, "date": None}


def _get_flexitime_sum_from_attendance(
	employee: str, from_date: str | None = None, to_date: str | None = None
) -> float:
	""" """
	filters = [
		["employee", "=", employee],
		["docstatus", "=", 1],
	]
	if from_date:
		filters.append(["attendance_date", ">=", from_date])
	if to_date:
		filters.append(["attendance_date", "<=", to_date])

	result = frappe.get_list(
		"Attendance",
		fields=["SUM(flexitime) as flexitime_sum"],
		filters=filters,
		as_list=True,
	)

	return result[0][0] if result and result[0][0] else 0


def beautify_report_data(working_time_summary: dict) -> dict:
	# Beautify the Flexitime Correction
	flexitime_correction = working_time_summary.get("flexitime_correction", {})
	if flexitime_correction.get("flexitime_hours") and flexitime_correction.get("date"):
		formatted_hours = _format_duration_hours(flexitime_correction.get("flexitime_hours"))
		formatted_date = frappe.utils.format_date(flexitime_correction.get("date"), "dd.MM.YYYY")
		flexitime_correction = _("{0} (on {1})").format(formatted_hours, formatted_date)
	else:
		flexitime_correction = "-"

	# Beautify the other values
	working_time_summary["flexitime_correction"] = flexitime_correction
	working_time_summary["current_balance"] = _format_duration_hours(
		working_time_summary.get("current_balance")
	)
	working_time_summary["future_balance_changes"] = _format_duration_hours(
		working_time_summary.get("future_balance_changes")
	)
	working_time_summary["future_balance"] = _format_duration_hours(
		working_time_summary.get("future_balance")
	)
	working_time_summary["open_time_captures"] = working_time_summary.get("open_time_captures")

	return working_time_summary


def _format_duration_hours(hours: float | None) -> str:
	"""
	Format float hours into a nice duration format.
	Examples:
	- 1.5 -> "1:30 h"
	- 7.5 -> "7:30 h"
	- 0.0 or None -> "0:00 h"
	- 1.024 -> "1:01 h" (rounded to nearest minute)
	"""
	if hours is None or hours == 0:
		return "0:00 h"

	# Handle negative values
	is_negative = hours < 0
	abs_hours = abs(hours)

	# Convert to hours and minutes
	total_hours = int(abs_hours)
	minutes = round((abs_hours % 1) * 60)

	# Handle minute overflow (e.g., 1.99 hours becomes 2:00h)
	if minutes >= 60:
		total_hours += 1
		minutes = 0

	# Add negative sign if needed
	sign = "-" if is_negative else ""
	return f"{sign}{total_hours}:{minutes:02d} h"
