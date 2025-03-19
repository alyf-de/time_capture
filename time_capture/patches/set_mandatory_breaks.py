import frappe


def execute():
	settings_doc = frappe.get_doc("Time Capture Settings")
	settings_doc.enforce_mandatory_breaks = 1
	settings_doc.extend(
		"mandatory_breaks",
		[
			{
				"working_time": 21600,
				"additional_break_time": 1800,
			},
			{
				"working_time": 32400,
				"additional_break_time": 900,
			},
		],
	)
	settings_doc.extend(
		"mandatory_breaks_minors",
		[
			{
				"working_time": 16200,
				"additional_break_time": 1800,
			},
			{
				"working_time": 21600,
				"additional_break_time": 1800,
			},
		]
	)
	settings_doc.flags.ignore_mandatory = True
	settings_doc.save()
