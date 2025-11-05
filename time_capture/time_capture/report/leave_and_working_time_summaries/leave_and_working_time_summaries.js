// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Leave and Working Time Summaries"] = {
	filters: [
		{
			fieldname: "status",
			fieldtype: "Select",
			label: __("Employee Status"),
			mandatory: 1,
			default: "Active",
			options: ["Active", "Inactive", "Suspended", "Left"],
		},
		{
			fieldname: "department",
			fieldtype: "Link",
			label: __("Department"),
			options: "Department",
		},
	],
};
