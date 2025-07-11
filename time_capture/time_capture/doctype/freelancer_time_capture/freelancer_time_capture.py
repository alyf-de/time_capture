# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

from time_capture.time_capture.time_capture_controller import (
	avoid_duplicate_entries,
	assure_duration_format,
	validate_time_log_description,
	validate_task_project,
	validate_tasks_budget,
	create_timesheets,
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
		if not "Freelancer" in frappe.get_roles(self.user):
			frappe.throw(
				_("Freelancer Time Capture can only be created for users with the 'Freelancer' role. Change the user in the field 'User'."),
				title=_("User is not a Freelancer"),
			)
