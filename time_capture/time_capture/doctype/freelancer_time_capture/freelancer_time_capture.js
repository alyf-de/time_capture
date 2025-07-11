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
