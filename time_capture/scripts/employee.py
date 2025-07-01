import frappe
from frappe import _
from frappe.utils import getdate


def before_validate(doc, method):
	validate_expected_working_hours(doc)


def validate_expected_working_hours(doc):
	if not doc.date_of_joining == min(getdate(ewh.valid_from) for ewh in doc.expected_working_hours):
		frappe.throw(_("Date of Joining is not the same as the earliest date of Expected Working Hours."))


def get_expected_working_hours(employee_id, date):
	"""
	Get the expected working hours for an employee on a specific date.
	"""
	return frappe.db.get_value(
		"Employee Expected Working Hours",
		filters={"parent": employee_id, "valid_from": ["<=", date]},
		fieldname="expected_daily_working_hours",
		order_by="valid_from desc",
	)
