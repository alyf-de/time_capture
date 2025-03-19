// Copyright (c) 2016, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Time"] = {
	filters: [
		{
			fieldname: "from_date",
			fieldtype: "Date",
			label: "From Date",
			mandatory: 1,
			default: moment().subtract(1, "week").startOf("isoWeek").format(),
		},
		{
			fieldname: "to_date",
			fieldtype: "Date",
			label: "To Date",
			mandatory: 1,
			default: moment().subtract(1, "week").endOf("isoWeek").format(),
		},
	],
};
