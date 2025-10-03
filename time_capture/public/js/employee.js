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
		if (frm.doc.name) {
			frm.add_custom_button(
				__("Time Capture & Leave Summary"),
				function () {
					// Reuse the existing function from utils.js
					time_capture.utils.show_leave_and_time_summary_for_employee(frm.doc);
				},
			);
		}
	},
});
