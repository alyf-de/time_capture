import frappe
from frappe import _
from frappe.query_builder import DocType


def execute():
	TimeCaptureLog = DocType("Time Capture Log")
	TimeCapture = DocType("Time Capture")

	time_logs = (
		frappe.qb.from_(TimeCaptureLog)
		.join(TimeCapture)
		.on(TimeCaptureLog.parent == TimeCapture.name)
		.select(
			TimeCaptureLog.name,
			TimeCaptureLog.parent,
			TimeCaptureLog.project,
			TimeCaptureLog.task,
			TimeCapture.date,
			TimeCapture.employee,
			TimeCapture.employee_name,
		)
		.where(TimeCapture.docstatus == 1)
	).run(as_dict=1)

	inconsistent_logs = []

	for log in time_logs:
		if log.task and log.project:
			task_project = frappe.db.get_value("Task", log.task, "project")
			if task_project != log.project:
				inconsistent_logs.append(log)

	if inconsistent_logs:
		error_message = "Inconsistent Time Capture Logs found:\n\n"
		for log in inconsistent_logs:
			error_message += f"Time Capture: {log.parent} ({log.date})\n"
			error_message += f"Employee: {log.employee_name} ({log.employee})\n"
			error_message += f"Log: {log.name}\n"
			error_message += f"Project: {log.project}\n"
			error_message += f"Task: {log.task}\n"
			error_message += "---\n"

		frappe.log_error(title="Inconsistent Time Capture Logs", message=error_message)
