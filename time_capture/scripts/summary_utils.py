import frappe


@frappe.whitelist()
def get_working_time_summary_for_employee(employee: str) -> dict:
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

	return {
		"flexitime_correction": flexitime_correction,
		"current_balance": current_balance,
		"future_balance_changes": future_balance_changes,
		"future_balance": future_balance,
		"open_time_captures": open_time_captures,
	}


def _get_last_flexitime_correction(employee: str) -> float:
	""" """
	flexitime_correction = frappe.db.get_value(
		"Flexitime Correction",
		filters={"employee": employee, "docstatus": 1},
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
