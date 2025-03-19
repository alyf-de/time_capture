import frappe
from frappe import _

from time_capture.time_capture.doctype.time_capture.time_capture import _create_time_capture


def on_submit(doc, event):
	delete_time_capture(doc)


def on_cancel(doc, event):
	employee = frappe.get_doc("Employee", doc.employee)
	_create_time_capture(employee, doc.attendance_date)


def delete_time_capture(doc):
	if not doc.leave_type or doc.attendance_date > frappe.utils.nowdate():
		return
	time_capture = frappe.db.get_all(
		"Time Capture",
		filters={
			"employee": doc.employee,
			"date": doc.attendance_date,
			"docstatus": 0,
			"working_time": 0,
		},
	)
	if time_capture:
		frappe.delete_doc("Time Capture", time_capture[0].name)
	else:
		message = "Keine löschbare Zeitfassung für Mitarbeiter {} am {} gefunden".format(
			doc.employee_name, doc.attendance_date
		)
		message += "<br><br>Mögliche Ursachen: Zeiterfassung wurde von einem System Manager gelöscht oder Mitarbeiter hat die Zeiterfassung bereits bearbeitet."
		frappe.log_error(
			title=_("Time Capture Not Found"),
			message=message,
			reference_doctype=doc.doctype,
			reference_name=doc.name,
		)
