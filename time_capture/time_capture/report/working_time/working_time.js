// Copyright (c) 2016, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Working Time"] = {
	filters: [
		{
			fieldname: "year",
			fieldtype: "Int",
			label: __("Year"),
			mandatory: 1,
			wildcard_filter: 0,
			default: moment().subtract(1, "month").year(),
		},
		{
			fieldname: "month",
			fieldtype: "Select",
			label: __("Month"),
			mandatory: 1,
			options: [
				{ value: 1, label: __("January") },
				{ value: 2, label: __("February") },
				{ value: 3, label: __("March") },
				{ value: 4, label: __("April") },
				{ value: 5, label: __("May") },
				{ value: 6, label: __("June") },
				{ value: 7, label: __("July") },
				{ value: 8, label: __("August") },
				{ value: 9, label: __("September") },
				{ value: 10, label: __("October") },
				{ value: 11, label: __("November") },
				{ value: 12, label: __("December") },
			],
			wildcard_filter: 0,
			default: moment().subtract(1, "month").month() + 1,
		},
	],
};
