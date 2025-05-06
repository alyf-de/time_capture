// Copyright (c) 2025, ALYF GmbH and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Bulk Leave Application", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Bulk Leave Application", {
	from_date: function (frm) {
		if (frm.doc.from_date && !frm.doc.to_date) {
			var a_year_from_start = frappe.datetime.add_months(frm.doc.from_date, 12);
			frm.set_value("to_date", frappe.datetime.add_days(a_year_from_start, -1));
		}
	},
});
