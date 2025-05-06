from datetime import date

import frappe
from frappe import _
from frappe.utils import getdate
from hrms.hr.utils import get_leave_period


def validate(doc, method=None):
	if doc.is_new():
		create_leave_policy_assignment(doc)
	elif not doc.is_new() and doc.has_value_changed("leave_policy"):
		frappe.msgprint(
			_(
				"Leave Policy has been changed. Note, that this will not update existing Leave Allocations or create/update future Leave Allocations."
			)
		)
		# A new feature is planned, that will regularly create new Leave Allocations for new periods.
		# TODO: Update this message when the feature is implemented.


def create_leave_policy_assignment(doc):
	year = getdate(doc.creation).year
	leave_period = get_leave_period(date(year, 1, 1), date(year, 12, 31), doc.company)

	leave_allocation = frappe.new_doc("Leave Policy Assignment")
	leave_allocation.employee = doc.employee
	leave_allocation.employee_name = doc.employee_name
	leave_allocation.leave_policy = doc.leave_policy
	leave_allocation.effective_from = date(year, 1, 1)
	leave_allocation.effective_to = date(year, 12, 31)
	leave_allocation.assignment_based_on = "Leave Period"
	leave_allocation.leave_period = leave_period[0].name
	leave_allocation.insert()
	leave_allocation.submit()
