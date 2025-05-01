# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.hr.utils import share_doc_with_approver, validate_active_employee


class BulkLeaveApplication(Document):
	def on_update_after_submit(self):
		if self.status == "Approved":
			self.create_leave_applications()

	def on_update(self):
		share_doc_with_approver(self, self.leave_approver)

	def create_leave_applications(self):
		for item in self.table_leaves:
			leave_application = frappe.new_doc("Leave Application")
			leave_application.employee = self.employee
			leave_application.leave_type = self.leave_type
			leave_application.leave_approver = self.leave_approver
			leave_application.posting_date = self.posting_date
			leave_application.status = self.status
			leave_application.from_date = item.from_date
			leave_application.to_date = item.to_date
			leave_application.reason = item.reason
			leave_application.follow_via_email = 0
			leave_application.insert()
			leave_application.submit()
