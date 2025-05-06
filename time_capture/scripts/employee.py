from datetime import date

import frappe
from frappe import _
from frappe.utils import getdate
from frappe.utils.data import today
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
	leave_period = get_leave_period(today(), today(), doc.company)

	leave_policy_assignment = frappe.new_doc("Leave Policy Assignment")
	leave_policy_assignment.employee = doc.employee
	leave_policy_assignment.employee_name = doc.employee_name
	leave_policy_assignment.leave_policy = doc.leave_policy
	leave_policy_assignment.effective_from = today()
	leave_policy_assignment.effective_to = date(year, 12, 31)
	leave_policy_assignment.assignment_based_on = "Leave Period"
	leave_policy_assignment.leave_period = leave_period[0].name
	leave_policy_assignment.insert()
	leave_policy_assignment.submit()
