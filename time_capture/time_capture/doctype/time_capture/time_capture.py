# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import math

import frappe
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from frappe import _
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds
from frappe.utils.data import getdate

FIVE_MINUTES = 5 * 60
ONE_HOUR = 60 * 60


class TimeCapture(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from time_capture.time_capture.doctype.time_capture_log.time_capture_log import TimeCaptureLog

		amended_from: DF.Link | None
		break_time: DF.Duration | None
		check_in: DF.Time
		check_out: DF.Time
		date: DF.Date
		email: DF.Data | None
		employee: DF.Link
		employee_name: DF.Data | None
		indicated_break: DF.Duration | None
		is_of_legal_age: DF.Check
		mandatory_break: DF.Duration | None
		time_logs: DF.Table[TimeCaptureLog]
		unallocated_time: DF.Duration | None
		working_time: DF.Duration | None

	# end: auto-generated types
	def before_insert(self):
		self.is_of_legal_age = self._get_is_of_legal_age()

	def before_validate(self):
		self.avoid_duplicate_entries()
		self.clean_data()
		self.assure_duration_format()
		self.calculate_totals()
		if self.has_value_changed("employee") or self.has_value_changed("date"):
			self.is_of_legal_age = self._get_is_of_legal_age()
		self.set_notification_email_address()

	def _get_is_of_legal_age(self):
		dob = frappe.db.get_value("Employee", self.employee, "date_of_birth")
		legal_age_date = frappe.utils.add_years(dob, 18)
		return legal_age_date <= frappe.utils.getdate(self.date)

	def assure_duration_format(self):
		note = _("Note: Use the date/time picker that appears instead of manually typing or pasting values.")
		row_msg = _("Row {0}: Duration is not in the proper format.")

		for log in self.time_logs:
			if isinstance(log.duration, float):
				log.duration = int(log.duration)
			if not isinstance(log.duration, int):
				frappe.throw(f"{row_msg.format(log.idx)} {note}")

		if self.indicated_break:
			if isinstance(self.indicated_break, float):
				self.indicated_break = int(self.indicated_break)
			if not isinstance(self.indicated_break, int):
				msg = _("Indicated Break is not in the proper format.")
				frappe.throw(f"{msg} {note}")

	def validate(self):
		self.validate_time_logs()
		self.validate_task_project()

	def before_submit(self):
		self.validate_working_and_project_time()
		self.validate_tasks_budget()

	def on_submit(self):
		self.create_attendance()
		self.create_timesheets()

	def validate_working_and_project_time(self):
		if self.unallocated_time > 0:
			frappe.throw(_("Working time must be completely booked on projects and tasks."))
		if self.unallocated_time < 0:
			frappe.throw(_("Project time cannot be greater than working time."))

	def validate_tasks_budget(self):
		tasks = {row.task for row in self.time_logs}
		for task in tasks:
			task_data = frappe.db.get_value("Task", task, ["expected_time", "actual_time"], as_dict=True)
			if task_data.expected_time == 0:
				continue
			if task_data.expected_time < task_data.actual_time:
				frappe.throw(
					_("No budget left for Task {0}. Please, contact the Project Manager.").format(task)
				)

	def validate_time_logs(self):
		for time_log in self.time_logs:
			if len(time_log.note) < 5:
				frappe.throw(_("Note must be at least 5 characters. Found: {0}").format(time_log.note))

	def avoid_duplicate_entries(self):
		if frappe.db.exists(
			"Time Capture",
			{
				"date": self.date,
				"employee": self.employee,
				"docstatus": ["!=", 2],
				"name": ["!=", self.name],
			},
		):
			frappe.throw(_("Time Capture already exists for this date and employee."))

	def clean_data(self):
		self.indicated_break = self.indicated_break or 0

	def calculate_totals(self):
		total_duration = time_diff_in_seconds(self.check_out, self.check_in)
		self.mandatory_break = get_mandatory_break(total_duration, self.is_of_legal_age)
		self.break_time = self.indicated_break or self.mandatory_break
		self.working_time = total_duration - self.break_time
		self.unallocated_time = self.working_time - sum(row.duration for row in self.time_logs)

	def set_notification_email_address(self):
		if not self.has_value_changed("employee"):
			return
		self.email = frappe.db.get_value("Employee", self.employee, "user_id") or frappe.db.get_single_value(
			"Time Capture Settings", "standard_email_recipient"
		)

	def create_attendance(self):
		if not frappe.db.exists(
			"Attendance",
			{
				"employee": self.employee,
				"attendance_date": self.date,
				"docstatus": ("!=", 2),
			},
		):
			working_hours = self.working_time / 60 / 60
			expected_working_hours = frappe.get_value(
				"Employee", self.employee, "expected_daily_working_hours"
			)
			if expected_working_hours:
				HALF_DAY = expected_working_hours / 2
				OVERTIME_FACTOR = 1.15
				MAX_HALF_DAY = HALF_DAY * OVERTIME_FACTOR * 60 * 60

			attendance = frappe.get_doc(
				{
					"doctype": "Attendance",
					"employee": self.employee,
					"status": "Present" if self.working_time > MAX_HALF_DAY else "Half Day",
					"attendance_date": self.date,
					"custom_time_capture": self.name,
					"working_hours": working_hours,
					"expected_working_hours": expected_working_hours,
					"flexitime": working_hours - expected_working_hours,
				}
			)
			attendance.flags.ignore_permissions = True
			attendance.save()
			attendance.submit()

	def create_timesheets(self):
		for log in self.time_logs:
			if log.duration and log.project:
				costing_rate = get_costing_rate(self.employee)
				hours = math.ceil(log.duration / FIVE_MINUTES) * FIVE_MINUTES / ONE_HOUR

				customer = frappe.get_value(
					"Project",
					log.project,
					["customer"],
				)

				is_billable = frappe.db.get_value("Task", log.task, "custom_hourly_billed") == 1
				billing_hours = hours if is_billable else 0

				timesheet = frappe.get_doc(
					{
						"doctype": "Timesheet",
						"time_logs": [
							{
								"is_billable": is_billable,
								"project": log.project,
								"task": log.task,
								"activity_type": get_default_activity_type(),
								"base_billing_rate": 0,
								"base_costing_rate": costing_rate,
								"costing_rate": costing_rate,
								"billing_rate": 0,
								"hours": hours,
								"from_time": self.date,
								"billing_hours": billing_hours,
								"description": log.note,
							}
						],
						"parent_project": log.project,
						"customer": customer,
						"employee": self.employee,
						"custom_time_capture": self.name,
					}
				)

				timesheet.insert()
				timesheet.submit()

	def validate_task_project(self):
		for log in self.time_logs:
			if log.project != frappe.db.get_value("Task", log.task, "project"):
				frappe.throw(_("Task {0} does not belong to Project {1}").format(log.task, log.project))


@frappe.whitelist()
def get_mandatory_break(duration: float, is_of_legal_age: bool):
	frappe.has_permission("Time Capture", "write", throw=True)
	settings = frappe.get_single("Time Capture Settings")

	if not settings.enforce_mandatory_breaks:
		return 0

	legal_thresholds = settings.mandatory_breaks if is_of_legal_age else settings.mandatory_breaks_minors
	mandatory_breaks = sorted((entry.working_time, entry.additional_break_time) for entry in legal_thresholds)

	total_mandatory_break = 0

	for threshold, mandatory_break in mandatory_breaks:
		if int(duration) - total_mandatory_break > threshold:
			total_mandatory_break += mandatory_break

	return total_mandatory_break


def get_default_activity_type():
	return frappe.db.get_single_value("Time Capture Settings", "default_activity_type")


def get_costing_rate(employee):
	return frappe.get_value(
		"Activity Cost",
		{"activity_type": get_default_activity_type(), "employee": employee},
		"costing_rate",
	)


def create_time_captures_daily():
	employees = _get_active_employees()
	today = frappe.utils.today()
	for employee in employees:
		_create_time_capture(employee, today)


def send_weekly_time_capture_reminders():
	if not frappe.db.get_single_value("Time Capture Settings", "enable_weekly_reminders"):
		return

	today = getdate()

	time_captures = frappe.get_all(
		"Time Capture",
		filters={"docstatus": 0, "date": ["<=", today]},
		fields=["name", "employee", "employee_name", "date", "email"],
		order_by="employee asc, date asc",
	)

	if not time_captures:
		return

	employees = {tc.employee for tc in time_captures}

	for employee in employees:
		tcs_list = [tc for tc in time_captures if tc.employee == employee]
		if not tcs_list:
			continue

		context = {"employee_name": tcs_list[0].employee_name, "time_entries": tcs_list}

		message = frappe.render_template("time_capture/templates/time_capture_reminder.html", context)
		frappe.sendmail(
			recipients=[tcs_list[0].email],
			subject="Wöchentliche Erinnerung: Offene Zeiterfassungen",
			message=message,
			now=True,
		)


def _get_active_employees():
	return frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "holiday_list"],
	)


def _create_time_capture(employee, date):
	if frappe.db.exists(
		"Time Capture",
		{
			"date": date,
			"employee": employee.name,
			"docstatus": ["!=", 2],
		},
	):
		return
	if frappe.db.exists(
		"Attendance",
		{
			"employee": employee.name,
			"attendance_date": date,
			"docstatus": 1,
		},
	):
		return
	if is_holiday(employee.holiday_list, date):
		return

	time_capture = frappe.new_doc("Time Capture")
	time_capture.update(
		{
			"doctype": "Time Capture",
			"employee": employee.name,
			"date": date,
			"check_in": "00:00",
			"check_out": "00:00",
		}
	)
	time_capture.insert()
