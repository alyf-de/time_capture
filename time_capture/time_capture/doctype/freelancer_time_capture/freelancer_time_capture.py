# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from time_capture.time_capture.time_capture_controller import (
	assure_duration_format,
	avoid_duplicate_entries,
	create_timesheets,
	validate_task_project,
	validate_tasks_budget,
	validate_time_log_description,
)


class FreelancerTimeCapture(Document):
	def before_validate(self):
		self.validate_user()
		avoid_duplicate_entries(self)
		assure_duration_format(self)
		validate_time_log_description(self)
		validate_task_project(self)

	def before_submit(self):
		validate_tasks_budget(self)
		create_timesheets(self)

	def validate_user(self):
		if "Freelancer" not in frappe.get_roles(self.user):
			frappe.throw(
				_(
					"Freelancer Time Capture can only be created for users with the 'Freelancer' role. Change the user in the field 'User'."
				),
				title=_("User is not a Freelancer"),
			)
