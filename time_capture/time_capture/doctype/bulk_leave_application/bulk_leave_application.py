# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.data import today
from hrms.hr.utils import share_doc_with_approver


class BulkLeaveApplication(Document):
	def on_update(self):
		share_doc_with_approver(self, self.leave_approver)

	def on_submit(self):
		if self.status in ["Open", "Cancelled"]:
			frappe.throw(_("Only Leave Applications with status 'Approved' and 'Rejected' can be submitted"))
		if self.status == "Approved":
			self.create_leave_applications()

	def before_cancel(self):
		self.status = "Cancelled"

	@frappe.whitelist()
	def get_weekly_off_dates(self):
		if not self.weekly_off:
			frappe.throw(_("Please select weekly off day"))
		for d in self.get_weekly_off_date_list(self.from_date, self.to_date):
			self.append("table_leaves", {"reason": _(self.weekly_off), "from_date": d, "to_date": d})

	def get_weekly_off_date_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		import calendar
		from datetime import timedelta

		from dateutil import relativedelta

		date_list = []
		existing_date_list = []
		weekday = getattr(calendar, (self.weekly_off).upper())
		reference_date = start_date + relativedelta.relativedelta(weekday=weekday)

		existing_date_list = [getdate(row.from_date) for row in self.get("table_leaves")]

		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
			reference_date += timedelta(days=7)

		holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")
		holidays = frappe.get_all("Holiday", filters={"parent": holiday_list, "holiday_date": ["between", [start_date, end_date]]}, pluck="holiday_date")
		date_list = [d for d in date_list if d not in holidays]
		return date_list

	def create_leave_applications(self):
		for item in self.table_leaves:
			leave_application = frappe.new_doc("Leave Application")
			leave_application.employee = self.employee
			leave_application.leave_type = self.leave_type
			leave_application.leave_approver = self.leave_approver
			leave_application.posting_date = today()
			leave_application.status = self.status
			leave_application.from_date = item.from_date
			leave_application.to_date = item.to_date
			leave_application.reason = item.reason
			leave_application.follow_via_email = 0
			leave_application.bulk_leave_application = self.name
			leave_application.insert()
			leave_application.submit()
