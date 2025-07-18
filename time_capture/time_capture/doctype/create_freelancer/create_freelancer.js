// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Create Freelancer", {
	refresh(frm) {
		frm.disable_save();

		frm.add_custom_button(__("Create Freelancer User"), function () {
			const email = frm.doc.email;
			const first_name = frm.doc.first_name;
			const last_name = frm.doc.last_name;

			if (!email || !first_name || !last_name) {
				frappe.throw(__("Please, set all fields."));
				return;
			}

			frappe.show_progress(__("Creating Freelancer User"), 0, __("Please wait..."));

			frm.call({
				method: "time_capture.time_capture.doctype.create_freelancer.create_freelancer.create_freelancer_user",
				args: {
					email: email,
					first_name: first_name,
					last_name: last_name,
				},
				callback: function (r) {
					frappe.hide_progress();
					if (r.exc) {
						frappe.msgprint(r.exc[0], "Error");
					} else {
						// Clear the form after successful creation
						frm.set_value("email", "");
						frm.set_value("first_name", "");
						frm.set_value("last_name", "");
						frm.set_value("description", "");
						frm.save();
					}
				},
			});
		});
	},
});
