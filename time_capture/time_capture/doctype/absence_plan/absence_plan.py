# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form, getdate
from frappe.utils.data import add_to_date
from hrms.hr.utils import share_doc_with_approver


class AbsencePlan(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from time_capture.time_capture.doctype.absence_plan_date.absence_plan_date import (
			AbsencePlanDate,
		)

		amended_from: DF.Link | None
		employee: DF.Link
		employee_name: DF.Data | None
		from_date: DF.Date | None
		leave_approver: DF.Link
		leave_type: DF.Link
		status: DF.Literal["Open", "Approved", "Rejected", "Cancelled"]
		dates: DF.Table[AbsencePlanDate]
		to_date: DF.Date | None
	# end: auto-generated types

	def after_insert(self):
		self.notify_leave_approver()

	def before_validate(self):
		self.remove_duplicate_dates()
		if self.dates:
			self.from_date = min([row.date for row in self.dates])
			self.to_date = max([row.date for row in self.dates])
		self.order_dates()

	def validate(self):
		self.avoid_overlapping_absence_plans()

	def on_update(self):
		share_doc_with_approver(self, self.leave_approver)

	def before_update_after_submit(self):
		self.order_dates()
		self.avoid_overlapping_absence_plans()

	def on_submit(self):
		if self.status in ["Open", "Cancelled"]:
			frappe.throw(_("Only Absence Plans with status 'Approved' and 'Rejected' can be submitted"))
		self.notify_employee()

	def before_cancel(self):
		self.status = "Cancelled"

	def remove_duplicate_dates(self):
		"""Keep only the first occurrence of each date in dates."""
		seen = set()
		new_rows = []
		for row in self.dates or []:
			key = str(row.date) if row.date else None
			if key is None:
				new_rows.append(row)
			elif key not in seen:
				seen.add(key)
				new_rows.append(row)
		self.dates = new_rows

	def order_dates(self):
		self.dates = sorted(self.dates, key=lambda x: x.date)

	def avoid_overlapping_absence_plans(self):
		overlapping_absence_plans = frappe.db.get_all(
			"Absence Plan",
			{"docstatus": ["!=", 2], "employee": self.employee, "name": ["!=", self.name]},
			or_filters={
				"from_date": ["between", [self.from_date, self.to_date]],
				"to_date": ["between", [self.from_date, self.to_date]],
			},
		)
		if overlapping_absence_plans:
			frappe.throw(
				_(
					"There is already an Absence Plan for this employee for the selected date range. See here: {0}"
				).format(
					get_link_to_form(
						"Absence Plan", overlapping_absence_plans[0].name, _("Absence Plans (List)")
					)
				)
			)
		return

	def notify_leave_approver(self):
		message = _("{0} raised a new Absence Plan for approval: {1}").format(
			self.employee_name or self.employee, self.name
		)
		_create_pwa_notification(self.leave_approver, self.employee, "Leave Approver", message, self.name)

	def notify_employee(self):
		message = _("Your Absence Plan {0} has been {1}.").format(
			self.name, _("Approved" if self.status == "Approved" else "Rejected")
		)
		_create_pwa_notification(self.leave_approver, self.employee, "Employee", message, self.name)


@frappe.whitelist()
def bulk_insert_dates(mode, from_date, to_date, weekday=None, reason=None):
	"""Return list of {date, reason} to add. Called from Bulk Insert dialog."""
	frappe.has_permission("Absence Plan", "write", throw=True)
	from_date = getdate(from_date)
	to_date = getdate(to_date)
	if to_date < from_date:
		frappe.throw(_("To Date cannot be before From Date."))
	if from_date < getdate():
		frappe.throw(_("Dates cannot be in the past."))

	if mode == "Weekly Off":
		if not weekday:
			frappe.throw(_("Please select at least one weekday"))
		return _get_weekly_off_dates(from_date, to_date, weekday)
	elif mode == "Timespan":
		return _get_timespan_days(from_date, to_date, reason)

	frappe.throw(_("Invalid mode"))


def _get_weekly_off_dates(from_date, to_date, weekday):
	weekdays = {
		"Monday": 0,
		"Tuesday": 1,
		"Wednesday": 2,
		"Thursday": 3,
		"Friday": 4,
		"Saturday": 5,
		"Sunday": 6,
	}
	weekday_index = weekdays[weekday]
	dates = []
	dt = from_date
	while dt <= to_date:
		if dt.weekday() == weekday_index:
			dates.append({"date": str(dt), "reason": weekday})
		dt = add_to_date(dt, days=1)
	return dates


def _get_timespan_days(from_date, to_date, reason=None):
	dates = []
	dt = from_date
	while dt <= to_date:
		dates.append({"date": str(dt), "reason": reason})
		dt = add_to_date(dt, days=1)
	return dates


def _create_pwa_notification(
	leave_approver: str, employee: str, send_to: str, message: str, absence_plan_name: str
):
	employee_user = frappe.db.get_value("Employee", employee, "user_id", cache=True)
	if send_to == "Leave Approver":
		from_user = leave_approver
		to_user = employee_user
	elif send_to == "Employee":
		from_user = employee_user
		to_user = leave_approver
	else:
		frappe.throw(_("Send to has to be either 'Leave Approver' or 'Employee'."))

	if not employee_user or not leave_approver:
		return

	if from_user == to_user:
		return

	n = frappe.new_doc("PWA Notification")
	n.from_user = from_user
	n.to_user = to_user
	n.message = message
	n.reference_document_type = "Absence Plan"
	n.reference_document_name = absence_plan_name
	n.insert(ignore_permissions=True)
