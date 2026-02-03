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

	leave_type: function (frm) {
		frappe.msgprint(
			__(
				"Warning: The Leave Ledgers will not be updated for leaves with an Absence Plan. Therefore, it is not suggested to use Leave Types (such as 'Annual Leave') that have limited Leave Allocation."
			)
		);
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
	const weekly_off_desc = __(
		"Weekly Off: adds all dates in the range that fall on the selected weekday. The Holiday List already defines non-working days; adding e.g. every Sunday as weekly off is often redundant."
	);
	const weekly_off_example_desc = __(
		"Typical use case: Every Friday is an unofficial weekly off day."
	);
	const weekly_off_exempt_desc = __(
		"Official weekly offs (e.g. 4 day work week set in employee contract) should be handled via Holiday List."
	);
	const timespan_desc = __("Timespan: adds all dates in the range with an optional reason.");
	const timespan_example_desc = __(
		"Typical use case: Employee is on Education Leave (University, School, etc.)."
	);
	const holiday_list_desc = __(
		"Holidays from a Holiday List have priority over leaves with an Absence Plan."
	);
	const warning_desc = __(
		"Warning: The Leave Ledgers will not be updated for leaves with an Absence Plan. Therefore, it is not suggested to use Leave Types (such as 'Annual Leave') that have limited Leave Allocation."
	);

	const descriptionHtml =
		"<p>" +
		weekly_off_desc +
		"<br>" +
		weekly_off_example_desc +
		"<br>" +
		weekly_off_exempt_desc +
		"</p><p>" +
		timespan_desc +
		"<br>" +
		timespan_example_desc +
		"</p><p>" +
		holiday_list_desc +
		"<br>" +
		warning_desc +
		"</p>";

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
				fieldtype: "HTML",
				fieldname: "description",
				label: __("Description"),
				options: descriptionHtml,
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
