# Copyright (c) 2013, ALYF GmbH and contributors
# For license information, please see license.txt
# Source: https://github.com/alyf-de/arbeitszeiterfassung_s4a/tree/develop/arbeitszeiterfassung_s4a/arbeitszeiterfassung_s4a/report/working_time

from datetime import date

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	return get_columns(), get_data(filters or {})


def get_data(filters: dict):
	working_time_summary = []
	employee_data = get_employees(filters)

	for row in employee_data:
		correction_hours, correction_date = get_flexitime_correction(row.employee)
		attendance_data = get_hours_from_attendance(row.employee, correction_date)

		actual = attendance_data.get("actual_working_hours") or 0
		expected = attendance_data.get("expected_working_hours") or 0
		balance = flt(actual - expected + (correction_hours or 0))
		working_time_summary.append(
			{
				"employee": row.employee,
				"employee_name": row.employee_name,
				"last_correction": correction_date,
				"correction_value": correction_hours,
				"expected_working_hours": expected,
				"actual_working_hours": actual,
				"balance": balance,
			}
		)

	return working_time_summary


def get_employees(filters: dict):
	"""Return a list of active employees."""
	emp_filters = [["status", "=", filters.get("status") or "Active"]]
	if department := filters.get("department"):
		emp_filters.append(["department", "=", department])

	return frappe.get_list(
		"Employee",
		filters=emp_filters,
		fields=["name as employee", "employee_name"],
		order_by="name ASC",
	)


def get_hours_from_attendance(employee: str, from_date: str = None) -> list[dict]:
	"""Return the total hours from attendance records."""
	filters = [
		["employee", "=", employee],
		["docstatus", "=", 1],
	]
	if from_date:
		filters.append(["attendance_date", ">=", from_date])

	attendance_hours = frappe.get_list(
		"Attendance",
		fields=[
			"SUM(expected_working_hours) as expected_working_hours",
			"SUM(working_hours) as actual_working_hours",
		],
		filters=filters,
	)

	return attendance_hours[0] if attendance_hours else {}


def get_flexitime_correction(employee: str) -> "tuple[float, date]":
	"""Return the last flexitime correction for the given employee."""
	filters = {"employee": employee, "docstatus": 1}
	if frappe.db.exists("Flexitime Correction", filters):
		return frappe.db.get_value(
			"Flexitime Correction",
			filters=filters,
			fieldname=["flexitime_hours", "date"],
			order_by="date DESC",
		)

	return (None, None)


def get_columns() -> list[dict]:
	return [
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"label": _("Employee"),
			"options": "Employee",
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
		},
		{
			"fieldname": "last_correction",
			"fieldtype": "Date",
			"label": _("Last Manual Correction"),
		},
		{
			"fieldname": "correction_value",
			"fieldtype": "Float",
			"label": _("Correction Value"),
		},
		{
			"fieldname": "expected_working_hours",
			"fieldtype": "Float",
			"label": _("Expected Working Hours"),
		},
		{
			"fieldname": "actual_working_hours",
			"fieldtype": "Float",
			"label": _("Actual Working Hours"),
		},
		{
			"fieldname": "balance",
			"fieldtype": "Float",
			"label": _("Balance"),
		},
	]
