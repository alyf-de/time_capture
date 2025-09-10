frappe.ui.form.on("Employee", {
	custom_update_attendances: function (frm) {
		frappe.call(
			"time_capture.scripts.employee.update_attendances_with_expected_working_hours",
			{
				employee_id: frm.doc.name,
			}
		);
	},
});

frappe.ui.form.on("Employee Expected Working Hours", {
	weekly_working_hours: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.weekly_working_hours) {
			let daily_hours = row.weekly_working_hours / 5;
			frappe.model.set_value(cdt, cdn, "monday", daily_hours);
			frappe.model.set_value(cdt, cdn, "tuesday", daily_hours);
			frappe.model.set_value(cdt, cdn, "wednesday", daily_hours);
			frappe.model.set_value(cdt, cdn, "thursday", daily_hours);
			frappe.model.set_value(cdt, cdn, "friday", daily_hours);

			frappe.show_alert({
				message: __("Updated Monday to Friday to {0} h each", [
					format_number(daily_hours),
				]),
				indicator: "green",
			});
		}
	},
});
