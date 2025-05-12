// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Bulk Leave Application", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Bulk Leave Application", {
	setup: function (frm) {
		frm.set_query("leave_approver", function () {
			return {
				query: "hrms.hr.doctype.department_approver.department_approver.get_approvers",
				filters: {
					employee: frm.doc.employee,
					doctype: "Leave Application",
				},
			};
		});
		frm.set_query("employee", erpnext.queries.employee);
	},

	from_date: function (frm) {
		if (frm.doc.from_date && !frm.doc.to_date) {
			var a_year_from_start = frappe.datetime.add_months(frm.doc.from_date, 12);
			frm.set_value("to_date", frappe.datetime.add_days(a_year_from_start, -1));
		}
	},

	employee: function (frm) {
		frm.trigger("set_leave_approver");
	},

	set_leave_approver: function (frm) {
		if (frm.doc.employee) {
			return frappe.call({
				method: "hrms.hr.doctype.leave_application.leave_application.get_leave_approver",
				args: {
					employee: frm.doc.employee,
				},
				callback: function (r) {
					if (r && r.message) {
						frm.set_value("leave_approver", r.message);
					}
				},
			});
		}
	},
});
	
	frappe.ui.form.on("Bulk Leave Application Date", {
		from_date: function (frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "to_date", locals[cdt][cdn].from_date);
	},
});

