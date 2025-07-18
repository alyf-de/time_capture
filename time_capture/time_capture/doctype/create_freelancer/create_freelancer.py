# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
import frappe.permissions
from frappe import _
from frappe.model.document import Document


class CreateFreelancer(Document):
	pass


@frappe.whitelist()
def create_freelancer_user(email: str, first_name: str, last_name: str):
	"""Create a new User with Freelancer role (incl. role, module and general settings)"""
	frappe.has_permission("User", "create", throw=True)
	try:
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
				"send_welcome_email": 1,
				"user_type": "System User",
				"default_workspace": "Freelancer",
			}
		)
		user.append("roles", {"role": "Freelancer"})
		user.insert()

		block_all_modules_except_time_capture(user)
		user.save()

		create_user_permission(user.name)

	except Exception as e:
		frappe.throw(_("Error creating freelancer user: {0}").format(str(e)))


def create_user_permission(user_name: str):
	"""Create User Permission on User for the created user"""
	try:
		frappe.permissions.add_user_permission(
			doctype="User", name=user_name, user=user_name, applicable_for="User"
		)
	except Exception as e:
		frappe.log_error(f"Error creating User Permission for {user_name}: {e!s}")


def block_all_modules_except_time_capture(user: Document):
	"""Block all modules except Time Capture for the user"""
	try:
		all_modules = frappe.get_all("Module Def", fields=["name"])

		for module in all_modules:
			if module.name != "Time Capture":
				user.append("block_modules", {"module": module.name})

	except Exception as e:
		frappe.log_error(f"Error blocking modules for user {user.name}: {e!s}")
