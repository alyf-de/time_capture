// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

function set_task_query(frm) {
	frm.fields_dict["time_logs"].grid.get_field("task").get_query = function (frm, cdt, cdn) {
		const child = locals[cdt][cdn];
		return {
			query: "time_capture.time_capture.doctype.time_capture.time_capture.task_query",
			filters: {
				project: child.project,
				status: ["!=", "Cancelled"],
				custom_is_active: "Yes",
			},
		};
	};
}
