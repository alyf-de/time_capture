# Copyright (c) 2013, ALYF GmbH and contributors
# For license information, please see license.txt

from collections import defaultdict
from datetime import date

import frappe
from frappe.utils.dateutils import get_last_day

PAID_LEAVE = "Bezahlter Urlaub"
SICK_LEAVE = "Krankheitsbedingte Abwesenheit"

COLUMNS = [
	{
		"fieldname": "employee",
		"fieldtype": "Link",
		"label": "Employee",
		"options": "Employee",
	},
	{
		"fieldname": "employee_name",
		"fieldtype": "Data",
		"label": "Employee Name",
	},
	{
		"fieldname": "expected_working_hours",
		"fieldtype": "Float",
		"label": "Expected Working Hours",
	},
	{
		"fieldname": "working_hours",
		"fieldtype": "Float",
		"label": "Working Hours",
	},
	{
		"fieldname": "flexitime_change",
		"fieldtype": "Float",
		"label": "Flexitime Change",
	},
	{
		"fieldname": "flexitime_hours",
		"fieldtype": "Float",
		"label": "Flexitime Hours",
	},
	{
		"fieldname": "paid_holidays",
		"fieldtype": "Int",
		"label": "Paid Holidays",
	},
	{
		"fieldname": "sick_days",
		"fieldtype": "Int",
		"label": "Sick Days",
	},
	{
		"fieldname": "other_absence_days",
		"fieldtype": "Int",
		"label": "Other Absence Days",
	},
]


def execute(filters=None):
	month_start_date = date(year=filters.year, month=int(filters.month), day=1)
	month_end_date = get_last_day(month_start_date)

	return COLUMNS, get_data(month_start_date, month_end_date)


def get_data(month_start_date, month_end_date):
	def assign(target, source, fields, default):
		data = source.get(target.employee, {})
		for field_type in fields:
			target[field_type] = data.get(field_type, default)

	employee_data = get_employees(month_start_date)
	attendance = get_attendance(month_start_date, month_end_date)
	leave_count = get_leave_count(month_start_date, month_end_date)

	for row in employee_data:
		attendance_fields = (
			"working_hours",
			"expected_working_hours",
			"flexitime_change",
		)
		assign(row, attendance, attendance_fields, 0.0)

		row["flexitime_hours"] = get_flexitime(row.employee, month_end_date)

		leave_types = ("paid_holidays", "sick_days", "other_absence_days")
		assign(row, leave_count, leave_types, 0)

	return employee_data


def get_employees(from_date):
	"""Return a list of active employees."""
	return frappe.get_list(
		"Employee",
		or_filters=[
			["relieving_date", "is", "not set"],
			["relieving_date", ">=", from_date],
		],
		fields=["name as employee", "employee_name"],
		order_by="name ASC",
	)


def get_attendance(from_date, to_date):
	"""Return a list of employees with their expected and actual working hours."""
	attendance = frappe.get_list(
		"Attendance",
		filters={"attendance_date": ("between", (from_date, to_date)), "docstatus": 1},
		fields=[
			"employee",
			"SUM(working_hours) as working_hours",
			"SUM(expected_working_hours) as expected_working_hours",
			"SUM(flexitime) as flexitime_change",
		],
		group_by="employee",
	)
	return {
		row.employee: {
			"working_hours": row.working_hours,
			"expected_working_hours": row.expected_working_hours,
			"flexitime_change": row.flexitime_change,
		}
		for row in attendance
	}


def get_flexitime(employee: str, to_date: date) -> float:
	"""Return a dictionary with flexitime per employee, up to `end_date`."""
	correction_hours, correction_date = get_flexitime_correction(employee, to_date)
	flexitime_hours = get_flexitime_from_attendance(employee, to_date, correction_date)

	return (correction_hours or 0.0) + (flexitime_hours or 0.0)


def get_flexitime_from_attendance(employee: str, to_date: date, from_date: str = None) -> float:
	filters = [
		["attendance_date", "<=", to_date],
		["employee", "=", employee],
		["docstatus", "=", 1],
	]
	if from_date:
		filters.append(["attendance_date", ">=", from_date])

	flexitime_hours = frappe.get_list(
		"Attendance",
		fields=["SUM(flexitime) as flexitime_hours"],
		filters=filters,
		as_list=True,
	)

	return flexitime_hours[0][0]


def get_flexitime_correction(employee: str, to_date: date) -> "tuple[float, date]":
	filters = {"employee": employee, "docstatus": 1, "date": ("<=", to_date)}
	if frappe.db.exists("Flexitime Correction", filters):
		return frappe.db.get_value(
			"Flexitime Correction",
			filters=filters,
			fieldname=["flexitime_hours", "date"],
			order_by="date DESC",
		)

	return (None, None)


def get_leave_count(from_date, to_date):
	"""Return a list of employees with the number of leaves they took."""
	# paid holidays and sick days
	leaves = frappe.get_list(
		"Attendance",
		filters={
			"attendance_date": ("between", (from_date, to_date)),
			"leave_type": (
				"in",
				(PAID_LEAVE, SICK_LEAVE),
			),
			"docstatus": 1,
		},
		fields=["employee", "leave_type", "count(leave_type) as leave_count"],
		group_by="employee,leave_type",
	)

	# other leaves
	leaves += frappe.get_list(
		"Attendance",
		filters={
			"attendance_date": ("between", (from_date, to_date)),
			"leave_type": (
				"not in",
				(PAID_LEAVE, SICK_LEAVE, ""),
			),
			"docstatus": 1,
		},
		fields=[
			"employee",
			"'other_absence_days' as leave_type",
			"count(leave_type) as leave_count",
		],
		group_by="employee,leave_type",
	)

	# convert to dictionary for easy lookup by employee
	result = defaultdict(dict)
	for row in leaves:
		if row["leave_type"] == PAID_LEAVE:
			fieldname = "paid_holidays"
		elif row["leave_type"] == SICK_LEAVE:
			fieldname = "sick_days"
		else:
			fieldname = "other_absence_days"

		result[row["employee"]][fieldname] = row["leave_count"]

	return dict(result)
