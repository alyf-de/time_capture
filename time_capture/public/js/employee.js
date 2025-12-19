frappe.ui.form.on("Employee", {
	custom_change_expected_hours: function (frm) {
		// Check if the employee is local or dirty.
		if (frm.doc.__islocal || frm.is_dirty()) {
			frappe.msgprint(__("Please save the Employee first."));
			return;
		}

		// only allow "System Manager" role to edit.
		if (!frappe.user_roles.includes("System Manager")) {
			frappe.msgprint(__("Only System Manager are allowed to edit Expected Working Hours."));
			return;
		}

		// Get current expected working hours data
		const current_data = (frm.doc.expected_working_hours || []).map((row) => {
			return {
				valid_from: row.valid_from,
				expected_daily_working_hours: row.expected_daily_working_hours,
			};
		});

		// Get child table fields
		frappe.model.with_doctype("Employee Expected Working Hours", () => {
			const child_fields = frappe.meta.get_docfields("Employee Expected Working Hours");

			// Create dialog
			const dialog = new frappe.ui.Dialog({
				title: __("Change/Add Expected Hours"),
				size: "large",
				fields: [
					{
						fieldname: "expected_working_hours",
						fieldtype: "Table",
						label: __("Expected Working Hours"),
						reqd: 1,
						data: current_data,
						get_data: () => {
							return current_data;
						},
						fields: child_fields.filter((df) => {
							return (
								!frappe.model.no_value_type.includes(df.fieldtype) &&
								!df.hidden &&
								df.fieldname !== "name"
							);
						}),
					},
				],
				primary_action: function () {
					const values = this.get_values();
					const expected_working_hours = values.expected_working_hours || [];

					if (expected_working_hours.length === 0) {
						frappe.msgprint(
							__("At least one Expected Working Hours entry is required.")
						);
						return;
					}

					const dialog_ref = this;
					frappe.call({
						method: "time_capture.scripts.employee.save_expected_working_hours_and_update_attendances",
						freeze: true,
						args: {
							employee_id: frm.doc.name,
							expected_working_hours: expected_working_hours,
						},
						callback: function (r) {
							frm.reload_doc();
							dialog_ref.hide();
						},
					});
				},
				primary_action_label: __("Save & Update Attendances"),
			});

			dialog.show();
		});
	},

	onload: function (frm) {
		if (frm.doc.name) {
			frm.add_custom_button(__("Time Capture & Leave Summary"), function () {
				// Reuse the existing function from utils.js
				time_capture.utils.show_leave_and_time_summary_for_employee(frm.doc);
			});
		}
	},
});
