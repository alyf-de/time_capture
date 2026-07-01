import math

import frappe
from frappe import _

FIVE_MINUTES = 5 * 60
ONE_HOUR = 60 * 60


def avoid_duplicate_entries(doc):
	"""
	Check if Time Capture or Freelancer Time Capture already exists for the same date and person.
	If it does, raise an error.
	"""
	filters = {
		"date": doc.date,
		"docstatus": ["!=", 2],
		"name": ["!=", doc.name],
	}
	if doc.doctype == "Freelancer Time Capture":
		filters["user"] = doc.user
	elif doc.doctype == "Time Capture":
		filters["employee"] = doc.employee

	if frappe.db.exists(doc.doctype, filters):
		frappe.throw(
			_("{0} already exists for this date and person.").format(doc.doctype),
			title=_("Duplicate Entry Found"),
		)


def assure_duration_format(doc):
	note = _("Note: Use the date/time picker that appears instead of manually typing or pasting values.")
	row_msg = _("Row {0}: Duration is not in the proper format.")

	for log in doc.time_logs:
		if isinstance(log.duration, float):
			log.duration = int(log.duration)
		if not isinstance(log.duration, int):
			frappe.throw(f"{row_msg.format(log.idx)} {note}")

	if doc.doctype == "Time Capture" and doc.indicated_break:
		if isinstance(doc.indicated_break, float):
			doc.indicated_break = int(doc.indicated_break)
		if not isinstance(doc.indicated_break, int):
			msg = _("Indicated Break is not in the proper format.")
			frappe.throw(f"{msg} {note}")


def validate_time_log_description(doc):
	for time_log in doc.time_logs:
		if len(time_log.note) < 5:
			frappe.throw(_("Note must be at least 5 characters. Found: {0}").format(time_log.note))


def validate_task_project(doc):
	for log in doc.time_logs:
		if log.project != frappe.db.get_value("Task", log.task, "project"):
			frappe.throw(_("Task {0} does not belong to Project {1}").format(log.task, log.project))


def validate_tasks_budget(doc):
	tasks = {row.task for row in doc.time_logs}
	for task in tasks:
		task_data = frappe.db.get_value("Task", task, ["expected_time", "actual_time"], as_dict=True)
		if task_data.expected_time == 0:
			continue
		if task_data.expected_time < task_data.actual_time:
			frappe.throw(_("No budget left for Task {0}. Please, contact the Project Manager.").format(task))


def create_timesheets(doc):
	for log in doc.time_logs:
		if log.duration and log.project:
			hours = math.ceil(log.duration / FIVE_MINUTES) * FIVE_MINUTES / ONE_HOUR

			customer = frappe.get_value(
				"Project",
				log.project,
				["customer"],
			)

			is_billable = frappe.db.get_value("Task", log.task, "custom_hourly_billed") == 1
			billing_hours = hours if is_billable else 0

			activity_type = _get_default_activity_type(doc.doctype)

			timesheet = frappe.get_doc(
				{
					"doctype": "Timesheet",
					"time_logs": [
						{
							"is_billable": is_billable,
							"project": log.project,
							"task": log.task,
							"activity_type": activity_type,
							"base_billing_rate": 0,
							"billing_rate": 0,
							"hours": hours,
							"from_time": doc.date,
							"billing_hours": billing_hours,
							"description": log.note,
						}
					],
					"parent_project": log.project,
					"company": frappe.db.get_value("Project", log.project, "company"),
					"customer": customer,
					"employee": doc.employee if doc.doctype == "Time Capture" else None,
					"freelancer_user": doc.user if doc.doctype == "Freelancer Time Capture" else None,
					"employee_name": _get_employee_name_for_timesheet(doc),
					"custom_time_capture": doc.name if doc.doctype == "Time Capture" else None,
					"freelancer_time_capture": doc.name if doc.doctype == "Freelancer Time Capture" else None,
				}
			)

			timesheet.flags.ignore_permissions = True
			timesheet.insert()
			timesheet.submit()


def _get_default_activity_type(for_doctype: str):
	if for_doctype == "Time Capture":
		return frappe.db.get_single_value("Time Capture Settings", "default_activity_type")
	elif for_doctype == "Freelancer Time Capture":
		return frappe.db.get_single_value("Time Capture Settings", "default_freelancer_activity_type")


def _get_employee_name_for_timesheet(doc):
	if doc.doctype == "Time Capture":
		return frappe.db.get_value("Employee", doc.employee, "employee_name")
	elif doc.doctype == "Freelancer Time Capture":
		return frappe.db.get_value("User", doc.user, "full_name")
	else:
		return None
