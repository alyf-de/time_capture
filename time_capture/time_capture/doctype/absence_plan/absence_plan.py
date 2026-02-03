# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt


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
		self.remove_past_dates()
		if self.dates:
			self.from_date = min([row.date for row in self.dates])
			self.to_date = max([row.date for row in self.dates])
		self.order_dates()

	def validate(self):
		self.avoid_duplicates_with_other_absence_plans()

	def on_update(self):
		share_doc_with_approver(self, self.leave_approver)

	def on_submit(self):
		if self.status in ["Open", "Cancelled"]:
			frappe.throw(_("Only Absence Plans with status 'Approved' and 'Rejected' can be submitted"))
		self.notify_employee()
		if self.status == "Approved":
			frappe.msgprint(
				_(
					"Absence Plan has been approved. The Employee will not have to capture any time for these dates."
				)
			)

	def before_cancel(self):
		if getdate(self.from_date) <= getdate():
			frappe.throw(
				_(
					"Absence Plan with dates in the past (or today) cannot be cancelled. Instead you can use the 'Delete Future Dates' button on top of the page. This will delete the future dates from the Absence Plan, but will not affect the past dates."
				)
			)
		self.status = "Cancelled"

	def notify_leave_approver(self):
		"""
		Notify leave approver about new Absence Plan
		"""
		# Preparation
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
		# Preparation
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

	def remove_past_dates(self):
		"""Remove dates that are in the past or today."""
		today = getdate()
		past_dates = []
		future_dates = []
		for row in self.dates:
			if getdate(row.date) <= today:
				past_dates.append(row)
			else:
				future_dates.append(row)
		self.dates = future_dates
		if past_dates:
			frappe.msgprint(
				_(
					"The following dates are in the past (or today) and have been removed from the Absence Plan:<br>{0}"
				).format("<br>".join([frappe.utils.format_date(row.date) for row in past_dates]))
			)

	def order_dates(self):
		self.dates = sorted(self.dates, key=lambda x: x.date)

	def avoid_duplicates_with_other_absence_plans(self):
		"""
		Check if the Absence Plan dates overlap with other Absence Plans for the same employee.
		Dates must be unique per employee; throw if any duplicate is found.
		"""
		other_plans = frappe.get_all(
			"Absence Plan",
			filters={"employee": self.employee, "name": ["!=", self.name or ""], "docstatus": ["!=", 2]},
			pluck="name",
		)
		if not other_plans:
			return

		our_dates = {getdate(row.date) for row in self.dates or [] if row.date}
		overlapping_dates = frappe.db.sql(
			"""
			SELECT apd.date, apd.parent
			FROM `tabAbsence Plan Date` apd
			WHERE apd.parent IN %(plans)s
			AND apd.date IN %(our_dates)s
			""",
			{"plans": other_plans, "our_dates": our_dates},
			as_dict=True,
		)

		if overlapping_dates:
			overlapping_dates_str = "<br>".join(
				[
					f"{frappe.utils.format_date(d.date)} in Absence Plan {frappe.utils.get_link_to_form('Absence Plan', d.parent)}"
					for d in overlapping_dates
				]
			)
			frappe.throw(
				_(
					"There are overlapping dates with following Absence Plans:<br>{0}",
				).format(overlapping_dates_str),
				title=_("Overlapping Dates are not allowed"),
			)


@frappe.whitelist()
def bulk_insert_dates(
	mode: str, from_date: str, to_date: str, weekday: str | None = None, reason: str | None = None
):
	"""Return list of {date, reason} to add. Called from Bulk Insert dialog."""
	from_date = getdate(from_date)
	to_date = getdate(to_date)
	if to_date < from_date:
		frappe.throw(_("To Date cannot be before From Date."))
	if from_date <= getdate():
		frappe.throw(_("Dates cannot be in the past or today."))

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


@frappe.whitelist()
def delete_future_dates(name: str) -> str:
	"""
	Delete all dates in the future from the Absence Plan child table and recalculate to_date.
	Requires Cancel permission. Only for submitted docs with from_date not in the future.
	"""
	doc = frappe.get_doc("Absence Plan", name)
	# Validations
	if doc.docstatus != 1:
		frappe.throw(_("Only submitted Absence Plans can use this action."))
	if getdate(doc.from_date) > getdate():
		frappe.throw(_("From Date is in the future. This means you can just cancel the whole Absence Plan."))
	if not doc.has_permission("cancel") and doc.leave_approver != frappe.session.user:
		frappe.throw(
			_("Only the Leave Approver and users with the 'Cancel' permission can delete future dates."),
			title=_("Permission Denied"),
		)

	# Delete future dates
	today = getdate()
	future_rows = [r for r in (doc.dates or []) if getdate(r.date) > today]
	deleted_count = 0
	for row in future_rows:
		frappe.delete_doc("Absence Plan Date", row.name)
		deleted_count += 1

	if deleted_count:
		doc.reload()
		remaining_dates = [getdate(r.date) for r in doc.dates if getdate(r.date) <= today]
		if remaining_dates:
			frappe.db.set_value(
				"Absence Plan",
				doc.name,
				{"from_date": min(remaining_dates), "to_date": max(remaining_dates)},
			)
		else:
			frappe.throw(_("All Dates are in the future. Please cancel the Absence Plan instead."))

	return _("Deleted {0} future date(s).").format(deleted_count)
