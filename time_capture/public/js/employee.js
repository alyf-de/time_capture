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
