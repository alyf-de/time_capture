frappe.ui.form.on("Employee", {
	custom_update_attendances: function (frm) {
		frappe.call(
			"time_capture.scripts.employee.update_attendances_with_expected_working_hours",
			{
				employee_id: frm.doc.name,
			}
		);
	},

	onload: function (frm) {
		// Add custom button to show time capture and leave summary
		if (frm.doc.name) {
			frm.add_custom_button(
				__("Show Summary"),
				function () {
					// Reuse the existing function from utils.js
					show_leave_and_time_summary(frm.doc);
				},
				__("Time Capture")
			);
		}
	},
});
