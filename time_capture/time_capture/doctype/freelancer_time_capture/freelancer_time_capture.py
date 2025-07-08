# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class FreelancerTimeCapture(Document):
	def before_validate(self):
		self.validate_user()

	def validate_user(self):
		if not "Freelancer" in frappe.get_roles(self.user):
			frappe.throw(
				_("Freelancer Time Capture can only be created for users with the 'Freelancer' role. Change the user in the field 'User'."),
				title=_("User is not a Freelancer"),
			)
