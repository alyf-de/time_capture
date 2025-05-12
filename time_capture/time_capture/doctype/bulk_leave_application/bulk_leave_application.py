# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.data import today

from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange

from hrms.hr.utils import share_doc_with_approver, get_holiday_dates_for_employee


class BulkLeaveApplication(Document):
	def on_update(self):
		share_doc_with_approver(self, self.leave_approver)

	def on_submit(self):
		if self.status in ["Open", "Cancelled"]:
			frappe.throw(_("Only Leave Applications with status 'Approved' and 'Rejected' can be submitted"))
		if self.status == "Approved":
			self.create_attendances()

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

		holidays = get_holiday_dates_for_employee(self.employee, start_date, end_date)
		date_list = [d for d in date_list if d not in holidays]
		return date_list

	def create_attendances(self):
		holidays = get_holiday_dates_for_employee(self.employee, self.from_date, self.to_date)
		for period in self.table_leaves: # TODO: Rename this!
			for dt in daterange(getdate(period.from_date), getdate(period.to_date)):
				if dt in holidays:
					continue
				attendance = frappe.new_doc("Attendance")
				attendance.employee = self.employee
				attendance.employee_name = self.employee_name
				attendance.attendance_date = str(dt)
				attendance.status = "On Leave"
				attendance.leave_type = self.leave_type
				attendance.insert()
				attendance.submit()
