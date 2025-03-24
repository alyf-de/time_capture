// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Working Time Summary"] = {
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
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!row || !["correction_value", "balance"].includes(column.fieldname)) {
			return value;
		}

		if (!data || !data[column.fieldname]) {
			return value;
		}

		if (data[column.fieldname] > 0) {
			return `<div style="color: green;">${value}</div>`;
		} else if (data[column.fieldname] < 0) {
			return `<div style="color: red;">${value}</div>`;
		}
		return value;
	},
};
