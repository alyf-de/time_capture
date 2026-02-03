// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Absence Plan", {
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
	},

	refresh: function (frm) {
		if (
			frm.doc.docstatus === 1 &&
			frm.doc.from_date &&
			frm.doc.from_date <= frappe.datetime.get_today()
		) {
			frm.add_custom_button(__("Delete Future Dates"), function () {
				frappe.call({
					method: "time_capture.time_capture.doctype.absence_plan.absence_plan.delete_future_dates",
					args: { name: frm.doc.name },
					callback: function (r) {
						if (r && r.message) {
							frappe.msgprint(r.message);
						}
						frm.reload_doc();
					},
				});
			});
		}
	},

	employee: function (frm) {
		frm.trigger("set_leave_approver");
	},

	bulk_insert_btn: function (frm) {
		open_bulk_insert_dialog(frm);
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

function open_bulk_insert_dialog(frm) {
	const d = new frappe.ui.Dialog({
		title: __("Bulk Insert"),
		fields: [
			{
				fieldtype: "Select",
				fieldname: "mode",
				label: __("Mode"),
				options: "Weekly Off\nTimespan",
				default: "Weekly Off",
				reqd: 1,
			},
			{
				fieldtype: "Date",
				fieldname: "from_date",
				label: __("From Date"),
				reqd: 1,
			},
			{
				fieldtype: "Date",
				fieldname: "to_date",
				label: __("To Date"),
				reqd: 1,
			},
			{
				fieldtype: "Select",
				fieldname: "weekday",
				label: __("Weekday"),
				options: "Monday\nTuesday\nWednesday\nThursday\nFriday\nSaturday\nSunday",
				depends_on: "eval:doc.mode === 'Weekly Off'",
				mandatory_depends_on: "eval:doc.mode === 'Weekly Off'",
			},
			{
				fieldtype: "Small Text",
				fieldname: "reason",
				label: __("Reason"),
				depends_on: "eval:doc.mode === 'Timespan'",
			},
		],
		primary_action_label: __("Add"),
		primary_action: function (values) {
			frappe.call({
				method: "time_capture.time_capture.doctype.absence_plan.absence_plan.bulk_insert_dates",
				args: {
					mode: values.mode,
					weekday: values.weekday,
					from_date: values.from_date,
					to_date: values.to_date,
					reason: values.reason,
				},
				callback: function (r) {
					if (r && r.message && r.message.length) {
						r.message.forEach(function (item) {
							const row = frm.add_child("dates");
							row.date = item.date;
							row.reason = item.reason || "";
						});
						frm.refresh_field("dates");
						frm.save();
					}
					d.hide();
				},
			});
		},
	});
	d.show();
}
