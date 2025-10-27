# Copyright (c) 2024, ALYF GmbH and contributors
# For license information, please see license.txt

import math
from itertools import groupby
from operator import itemgetter

import frappe
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_last_day, getdate, time_diff_in_seconds

from time_capture.time_capture.time_capture_controller import (
	assure_duration_format,
	avoid_duplicate_entries,
	create_timesheets,
	validate_task_project,
	validate_tasks_budget,
	validate_time_log_description,
)


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
	def before_validate(self):
		avoid_duplicate_entries(self)
		assure_duration_format(self)
		self.clean_data()
		self.calculate_totals()
		if self.has_value_changed("employee") or self.has_value_changed("date"):
			self.is_of_legal_age = self._get_is_of_legal_age()
		self.set_notification_email_address()

	def validate(self):
		validate_time_log_description(self)
		validate_task_project(self)

	def before_submit(self):
		self.validate_working_and_project_time()
		self.validate_time_to_submit_in_days()
		validate_tasks_budget(self)

	def on_submit(self):
		self.create_attendance()
		create_timesheets(self)

	def on_trash(self):
		frappe.db.set_value("Attendance", {"custom_time_capture": self.name}, "custom_time_capture", None)

	def validate_working_and_project_time(self):
		if self.unallocated_time > 0:
			frappe.throw(_("Working time must be completely booked on projects and tasks."))
		if self.unallocated_time < 0:
			frappe.throw(_("Project time cannot be greater than working time."))

	def clean_data(self):
		self.indicated_break = self.indicated_break or 0

	def _get_is_of_legal_age(self):
		dob = frappe.db.get_value("Employee", self.employee, "date_of_birth")
		legal_age_date = frappe.utils.add_years(dob, 18)
		return legal_age_date <= frappe.utils.getdate(self.date)

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
		"""
		Create Attendance if it doesn't exist.
		Update Attendance if it exists (For example if 'Absent' Attendance or sickday Atttendance was created before).
		"""
		filters = {
			"employee": self.employee,
			"attendance_date": self.date,
			"docstatus": ("!=", 2),
		}

		if not frappe.db.exists("Attendance", filters):
			working_hours = self.working_time / 60 / 60

			attendance = frappe.get_doc(
				{
					"doctype": "Attendance",
					"employee": self.employee,
					"attendance_date": self.date,
					"custom_time_capture": self.name,
					"working_hours": working_hours,
				}
			)
			attendance.flags.ignore_permissions = True
			attendance.save()
			attendance.submit()
		else:
			attendance = frappe.get_doc("Attendance", filters)
			attendance.working_hours = self.working_time / 60 / 60
			attendance.custom_time_capture = self.name
			attendance.flags.ignore_permissions = True
			attendance.save()

	def validate_time_to_submit_in_days(self):
		current_user_roles = frappe.get_user().get_roles()
		leave_approver = frappe.db.get_value("Employee", self.employee, "leave_approver")
		if (
			"System Manager" in current_user_roles
			or "Accountant" in current_user_roles
			or leave_approver == frappe.get_user().name
		):
			return

		time_to_submit_in_days = (
			frappe.get_single_value("Time Capture Settings", "time_to_submit_in_days") or 7
		)

		if frappe.utils.today() > frappe.utils.add_days(self.date, time_to_submit_in_days):
			frappe.throw(
				_(
					"Time Capture deadline missed. Please contact your supervisor to submit your Time Capture manually. (Time to submit: {0} days)"
				).format(time_to_submit_in_days)
			)


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


def create_time_captures_daily():
	employees = _get_active_employees()
	today = frappe.utils.today()
	for employee in employees:
		_create_time_capture(employee, today)


def send_reminders_for_unsubmitted_time_captures():
	settings = frappe.get_single("Time Capture Settings")
	if not settings.enable_weekly_reminders or not _send_reminders_today(settings):
		return

	# Calculate the cutoff date based on minimum draft age setting
	today = getdate()
	minimum_draft_age_days = settings.minimum_draft_age_days or 0
	minimum_draft_age_days = max(
		minimum_draft_age_days, 0
	)  # just in case someone set it to a negative number
	cutoff_date = frappe.utils.add_days(today, -minimum_draft_age_days)

	TC = frappe.qb.DocType("Time Capture")
	time_captures = (
		frappe.qb.from_(TC)
		.select(TC.name, TC.employee, TC.employee_name, TC.date)
		.where((TC.docstatus == 0) & (TC.date <= cutoff_date))
		.orderby(TC.employee, TC.date)
		.run(as_dict=True)
	)
	if not time_captures:
		return

	for emp, entries in groupby(time_captures, key=itemgetter("employee")):
		time_captures_per_employee = list(entries)

		recipient = frappe.db.get_value("Employee", emp, "user_id") or frappe.db.get_single_value(
			"Time Capture Settings", "standard_email_recipient"
		)
		language = frappe.db.get_value("User", recipient, "language") or "en"

		context = {
			"employee_name": time_captures_per_employee[0]["employee_name"],
			"time_captures_per_employee": time_captures_per_employee,
			"language": language,
		}
		message = frappe.render_template("time_capture/templates/time_capture_reminder.html", context)

		frappe.sendmail(
			recipients=recipient,
			subject=_("Reminder: You have unsubmitted Time Captures"),
			message=message,
			now=True,
		)
	frappe.db.set_value("Time Capture Settings", "last_notification_sent_on", today)


def _send_reminders_today(settings):
	"""
	This functions checks if the settings are set to send reminders today.
	It returns boolean.
	"""
	today = frappe.utils.getdate()
	if settings.notification_frequency == "Daily":
		return True

	if settings.notification_frequency == "Weekly":
		# Validate that today is the day of the week specified in the settings
		weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
		today_weekday = weekday_names[today.weekday()]
		return today_weekday == settings.notification_weekday

	if settings.notification_frequency == "Monthly":
		# Validate that the day of the month is the one defined in notification_day_of_the_month
		# If there is no such integer, then use the last day of the month
		if settings.notification_day_of_the_month:
			return today.day == settings.notification_day_of_the_month
		else:
			# Use the last day of the month
			last_day_of_month = get_last_day(today).day
			return today.day == last_day_of_month

	if settings.notification_frequency == "Every X Days":
		# If the last_notification_sent_on is smaller or same as today - settings.notification_interval_in_days, then return True
		if not settings.last_notification_sent_on:
			return True

		last_sent = frappe.utils.getdate(settings.last_notification_sent_on)
		days_since_last = frappe.utils.date_diff(today, last_sent)
		return days_since_last >= settings.notification_interval_in_days

	return False


def _get_active_employees():
	today = frappe.utils.today()
	return frappe.get_all(
		"Employee",
		filters={"status": "Active", "date_of_joining": ("<=", today)},
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
			"employee": employee.name,
			"date": date,
			"check_in": "00:00",
			"check_out": "00:00",
		}
	)
	time_capture.insert()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def task_query(doctype, txt, searchfield, start, page_len, filters):
	tasks = frappe.get_list(
		"Task",
		fields=["name", "subject", "expected_time", "actual_time"],
		filters=filters,
		or_filters=[["name", "like", f"%{txt}%"], ["subject", "like", f"%{txt}%"]],
		limit_start=start,
		limit_page_length=page_len,
		order_by="name asc",
	)

	results = []

	for task in tasks:
		expected = task.get("expected_time") or 0
		actual = task.get("actual_time") or 0

		if not expected:
			budget_value = "-"
		else:
			budget_value = f"{expected - actual:.2f} h"

		budget_display = _(f"Residual Budget: {budget_value}")
		label = task.get("subject") or task.get("name")
		results.append([task.get("name"), label, budget_display])

	return results
