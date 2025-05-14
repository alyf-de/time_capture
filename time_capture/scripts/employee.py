import frappe
from frappe import _


def before_validate(doc, method):
	validate_expected_working_hours(doc)


def validate_expected_working_hours(doc):
	if not doc.date_of_joining == min(ewh.valid_from for ewh in doc.expected_working_hours):
		frappe.throw(_("Date of Joining is not the same as the earliest date of Expected Working Hours."))
