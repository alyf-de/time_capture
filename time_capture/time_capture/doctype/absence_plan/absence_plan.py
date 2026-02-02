# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form, getdate
from frappe.utils.data import add_to_date
from hrms.hr.utils import share_doc_with_approver
from hrms.utils import get_employee_email


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

	def before_insert(self):
		self.employee_email = get_employee_email(self.employee)

	def after_insert(self):
		self.notify_leave_approver()

	def before_validate(self):
		self.remove_duplicate_dates()
		if self.dates:
			self.from_date = min([row.date for row in self.dates])
			self.to_date = max([row.date for row in self.dates])
		self.order_dates()

	def on_update(self):
		share_doc_with_approver(self, self.leave_approver)

	def on_submit(self):
		if self.status in ["Open", "Cancelled"]:
			frappe.throw(_("Only Absence Plans with status 'Approved' and 'Rejected' can be submitted"))
		self.notify_employee()

	def before_cancel(self):
		self.status = "Cancelled"

	def notify_leave_approver(self):
		"""
		Notify leave approver about new Absence Plan
		"""
		# Preperation
		if not self.leave_approver:
			return
		from_user = self.employee_email
		if from_user == self.leave_approver:
			return

		lang = _get_user_lang(self.leave_approver)
		message = _("{0} raised a new Absence Plan for approval: {1}", lang=lang).format(
			self.employee_name or self.employee, self.name
		)

		# Create Notification
		n = frappe.new_doc("PWA Notification")
		n.from_user, n.to_user = from_user, self.leave_approver
		n.message = message
		n.reference_document_type, n.reference_document_name = self.doctype, self.name
		n.insert(ignore_permissions=True)

		# Send Email
		link = get_link_to_form(self.doctype, self.name, _("Absence Plan", lang=lang))
		frappe.sendmail(
			recipients=[self.leave_approver],
			subject=_("Absence Plan {0} for approval", lang=lang).format(self.name),
			message=message + "<br><br>" + link,
		)
		frappe.msgprint(_("Leave approver {0} has been notified via Email.").format(self.leave_approver))

	def notify_employee(self):
		"""
		Notify employee about Absence Plan approval status
		"""
		# Preperation
		to_user = self.employee_email
		if not to_user:
			return
		from_user = self.leave_approver
		if from_user == to_user:
			return

		lang = _get_user_lang(to_user)
		message = _("Your Absence Plan {0} has been {1}.", lang=lang).format(self.name, self.status)

		# Create Notification
		n = frappe.new_doc("PWA Notification")
		n.from_user, n.to_user = from_user, to_user
		n.message = message
		n.reference_document_type, n.reference_document_name = self.doctype, self.name
		n.insert(ignore_permissions=True)

		# Send Email
		link = get_link_to_form(self.doctype, self.name, _("Absence Plan", lang=lang))
		frappe.sendmail(
			recipients=[to_user],
			subject=_("Absence Plan {0} - {1}", lang=lang).format(self.name, self.status),
			message=message + "<br><br>" + link,
		)
		frappe.msgprint(_("Employee {0} has been notified via Email.").format(to_user))

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


@frappe.whitelist()
def bulk_insert_dates(
	mode: str, from_date: str, to_date: str, weekday: str | None = None, reason: str | None = None
):
	"""Return list of {date, reason} to add. Called from Bulk Insert dialog."""
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


def _get_user_lang(user):
	user_lang = frappe.db.get_value("User", user, "language", cache=True)
	if user_lang:
		return user_lang
	return frappe.local.lang or "en"
