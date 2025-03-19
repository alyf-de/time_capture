// Copyright (c) 2016, ALYF GmbH and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Working Time"] = {
	filters: [
		{
			fieldname: "year",
			fieldtype: "Int",
			label: "Year",
			mandatory: 1,
			wildcard_filter: 0,
			default: moment().subtract(1, "month").year(),
		},
		{
			fieldname: "month",
			fieldtype: "Select",
			label: "Month",
			mandatory: 1,
			options: [
				{ value: 1, label: "January" },
				{ value: 2, label: "February" },
				{ value: 3, label: "March" },
				{ value: 4, label: "April" },
				{ value: 5, label: "May" },
				{ value: 6, label: "June" },
				{ value: 7, label: "July" },
				{ value: 8, label: "August" },
				{ value: 9, label: "September" },
				{ value: 10, label: "October" },
				{ value: 11, label: "November" },
				{ value: 12, label: "December" },
			],
			wildcard_filter: 0,
			default: moment().subtract(1, "month").month() + 1,
		},
	],
};
