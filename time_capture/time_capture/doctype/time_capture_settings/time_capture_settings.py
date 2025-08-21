# Copyright (c) 2025, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TimeCaptureSettings(Document):
	def before_validate(self):
		if self.notification_frequency == "Monthly" and self.notification_day_of_the_month:
			# has to be between 1 and 28
			if self.notification_day_of_the_month < 1 or self.notification_day_of_the_month > 28:
				frappe.throw(_("Notification day of the month has to be between 1 and 28"))
