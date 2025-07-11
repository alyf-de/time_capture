// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Freelancer Time Capture", {
	setup: function (frm) {
		set_task_query(frm);
	},
	refresh(frm) {
		if (!frm.doc.user && frappe.session.user) {
			frm.set_value("user", frappe.session.user);
		}
	},
});

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
