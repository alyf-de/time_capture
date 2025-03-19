# Copyright (c) 2013, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from ..working_time.working_time import get_employees

COLUMNS = [
	{
		"fieldname": "timesheet",
		"fieldtype": "Link",
		"label": "Timesheet",
		"options": "Timesheet",
		"width": 150,
	},
	{
		"fieldname": "start_date",
		"fieldtype": "Date",
		"label": "Start Date",
		"width": 100,
	},
	{
		"fieldname": "activity_type",
		"fieldtype": "Link",
		"label": "Activity Type",
		"options": "Activity Type",
	},
	{
		"fieldname": "description",
		"fieldtype": "Data",
		"label": "Description",
		"width": 300,
	},
	{
		"fieldname": "hours",
		"fieldtype": "Float",
		"label": "Hours",
		"precision": 2,
	},
	{
		"fieldname": "project",
		"fieldtype": "Link",
		"label": "Project",
		"options": "Project",
	},
	{
		"fieldname": "task",
		"fieldtype": "Link",
		"label": "Task",
		"options": "Task",
		"width": 150,
	},
	{
		"fieldname": "is_billable",
		"fieldtype": "Check",
		"label": "Is Billable",
	},
	{
		"fieldname": "sales_invoice",
		"fieldtype": "Link",
		"label": "Sales Invoice",
		"options": "Sales Invoice",
		"width": 150,
	},
]


def execute(filters=None):
	return COLUMNS, get_data(filters["from_date"], filters["to_date"])


def get_data(from_date: str, to_date: str):
	employees = get_employees(from_date)

	result = []
	for employee in employees:
		result.append(
			(
				None,
				None,
				None,
				frappe.bold(employee.employee_name),
				None,
				None,
				None,
				None,
				None,
			)
		)
		timesheets = frappe.get_list(
			"Timesheet",
			filters={
				"start_date": ("<=", to_date),
				"end_date": (">=", from_date),
				"employee": employee.employee,
			},
			fields=[
				"name",
				"start_date",
				"`tabTimesheet Detail`.activity_type",
				"`tabTimesheet Detail`.description",
				"`tabTimesheet Detail`.hours",
				"`tabTimesheet Detail`.project",
				"`tabTimesheet Detail`.task",
				"`tabTimesheet Detail`.is_billable",
				"`tabTimesheet Detail`.sales_invoice",
			],
			order_by="start_date ASC",
			as_list=True,
		)
		total_hrs = 0

		if timesheets:
			total_hrs = sum(row[4] for row in timesheets)
			result.extend(timesheets)

		result.append(
			(
				None,
				None,
				None,
				frappe.bold(_("Sum for {}").format(employee.employee_name)),
				total_hrs,
				None,
				None,
				None,
				None,
			)
		)

		result.append([None] * 9)

	return result
