import frappe


def execute():
	if frappe.db.exists("Role", "Freelancer"):
		print(
			"Role 'Freelancer' already exists, skipping creation. Please, adjust the roles + permissions manually if needed."
		)
		return
	_create_freelancer_role()
	_add_custom_docperm_for_freelancer_role()


def _create_freelancer_role():
	new_role_doc = frappe.new_doc("Role")
	new_role_doc.role_name = "Freelancer"
	new_role_doc.home_page = "/app/freelancer"
	new_role_doc.save()


def _add_custom_docperm_for_freelancer_role():
	"""
	Add custom DocPerm for the 'Freelancer' role for Project (Select), Task (Select) and Timesheet (Submit and less).
	"""
	project_docperm = frappe.new_doc("Custom DocPerm")
	project_docperm.role = "Freelancer"
	project_docperm.parent = "Project"
	project_docperm.select = 1
	project_docperm.save()

	task_docperm = frappe.new_doc("Custom DocPerm")
	task_docperm.role = "Freelancer"
	task_docperm.parent = "Task"
	task_docperm.select = 1
	task_docperm.save()

	timesheet_docperm = frappe.new_doc("Custom DocPerm")
	timesheet_docperm.role = "Freelancer"
	timesheet_docperm.parent = "Timesheet"
	timesheet_docperm.if_owner = 1
	timesheet_docperm.create = 1
	timesheet_docperm.submit = 1
	timesheet_docperm.read = 1
	timesheet_docperm.write = 1
	timesheet_docperm.save()
