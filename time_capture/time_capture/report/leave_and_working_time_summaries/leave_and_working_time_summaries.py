# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

from re import S

import frappe
from frappe import _

from time_capture.scripts.summary_utils import get_summary_for_employees


def execute(filters=None):
	return get_columns(), get_data(filters or {})


def get_data(filters: dict):
	"""
	Get summary data for all employees using the summary_utils function.
	"""
	# Build filters dict from report filters
	emp_filters = {}
	if status := filters.get("status"):
		emp_filters["status"] = status
	else:
		emp_filters["status"] = "Active"

	if department := filters.get("department"):
		emp_filters["department"] = department

	# Get beautified data for all employees
	summary_data = get_summary_for_employees(filters=emp_filters, beautified=True)

	# Format data for report
	report_data = []
	for row in summary_data:
		report_data.append(
			{
				"employee": row.get("employee"),
				"employee_name": row.get("employee_name"),
				"flexitime_correction": row.get("flexitime_correction", "-"),
				"current_balance": row.get("current_balance", "0:00 h"),
				"future_balance_changes": row.get("future_balance_changes", "0:00 h"),
				"future_balance": row.get("future_balance", "0:00 h"),
				"open_time_captures": row.get("open_time_captures", 0),
			}
		)

	return report_data


def get_columns() -> list[dict]:
	return [
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"label": _("Employee"),
			"options": "Employee",
			"width": 100,
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
			"width": 200,
		},
		{
			"fieldname": "flexitime_correction",
			"fieldtype": "Data",
			"label": _("Flexitime Correction"),
			"width": 220,
		},
		{
			"fieldname": "current_balance",
			"fieldtype": "Data",
			"label": _("Current Balance"),
			"width": 150,
			"align": "right",
		},
		{
			"fieldname": "future_balance_changes",
			"fieldtype": "Data",
			"label": _("Future Balance Changes"),
			"width": 200,
			"align": "right",
		},
		{
			"fieldname": "future_balance",
			"fieldtype": "Data",
			"label": _("Future Balance"),
			"width": 150,
			"align": "right",
		},
		{
			"fieldname": "open_time_captures",
			"fieldtype": "Int",
			"label": _("Open Time Captures"),
			"width": 180,
			"align": "right",
		},
	]
