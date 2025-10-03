# Copyright (c) 2013, ALYF GmbH and contributors
# For license information, please see license.txt
# Source: https://github.com/alyf-de/arbeitszeiterfassung_s4a/tree/develop/arbeitszeiterfassung_s4a/arbeitszeiterfassung_s4a/report/working_time

import frappe
from frappe import _

from time_capture.scripts.summary_utils import get_working_time_summary_for_employee


def execute(filters=None):
	return get_columns(), get_data(filters or {})


def get_data(filters: dict):
	working_time_summary = []
	employee_data = get_employees(filters)

	for row in employee_data:
		# Get summary data using the summary_utils function
		summary_data = get_working_time_summary_for_employee(row.employee, beautified=True)

		working_time_summary.append(
			{
				"employee": row.employee,
				"employee_name": row.employee_name,
				"flexitime_correction": summary_data.get("flexitime_correction", "-"),
				"current_balance": summary_data.get("current_balance", "0:00 h"),
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
			"width": 300,
		},
		{
			"fieldname": "flexitime_correction",
			"fieldtype": "Data",
			"label": _("Flexitime Correction"),
			"width": 300,
		},
		{
			"fieldname": "current_balance",
			"fieldtype": "Data",
			"label": _("Current Balance"),
		},
	]
