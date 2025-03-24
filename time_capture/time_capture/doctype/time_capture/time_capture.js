// Copyright (c) 2024, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Time Capture", {
	refresh: function (frm) {
		if (!frm.doc.employee && frappe.session.user && frappe.session.user !== "Administrator") {
			set_default_employee(frm);
		}
	},
	employee: set_is_of_legal_age,
	date: set_is_of_legal_age,
	check_in: handle_check_in_out,
	check_out: handle_check_in_out,
	mandatory_break: set_break_time,
	indicated_break: set_break_time,
	break_time: handle_duration_change,
	working_time: update_unallocated_time,
});

frappe.ui.form.on("Time Capture Log", {
	duration: update_unallocated_time,
	time_logs_add: function (frm, cdt, cdn) {
		const child = frappe.get_doc(cdt, cdn);
		child.duration = frm.doc.unallocated_time;
		frm.refresh_field("time_logs");
		update_unallocated_time(frm);
	},
	time_logs_remove: update_unallocated_time,
});

function set_is_of_legal_age(frm) {
	if (frm.doc.employee && frm.doc.date) {
		frappe.db.get_value("Employee", frm.doc.employee, "date_of_birth", (r) => {
			if (r && r.date_of_birth) {
				const dob = frappe.datetime.str_to_obj(r.date_of_birth);
				const reference_date = frappe.datetime.str_to_obj(frm.doc.date);
				const age = reference_date.getFullYear() - dob.getFullYear();
				const is_of_legal_age =
					age > 18 ||
					(age === 18 &&
						reference_date >=
							new Date(dob.getFullYear() + 18, dob.getMonth(), dob.getDate()))
						? 1
						: 0;
				frm.set_value("is_of_legal_age", is_of_legal_age);
			}
		});
	}
}

function handle_check_in_out(frm) {
	const duration = calculate_duration(frm.doc.check_in, frm.doc.check_out);
	update_mandatory_break(frm, duration);
	set_working_time(frm, duration);
}

function handle_duration_change(frm) {
	const duration = calculate_duration(frm.doc.check_in, frm.doc.check_out);
	set_working_time(frm, duration);
}

function set_default_employee(frm) {
	if (!frappe.model.can_read("Employee")) {
		return;
	}
	frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name").then((response) => {
		const employee = response?.message?.name;
		if (employee) {
			frm.set_value("employee", employee);
		}
	});
}

function calculate_duration(check_in, check_out) {
	return time_to_seconds(check_out) - time_to_seconds(check_in);
}

function time_to_seconds(time) {
	const [hours, minutes, seconds] = time.split(":").map(Number);
	return hours * 3600 + minutes * 60 + seconds;
}

function update_mandatory_break(frm, duration) {
	if (frm.doc.check_in && frm.doc.check_out) {
		frappe.call({
			method: "time_capture.time_capture.doctype.time_capture.time_capture.get_mandatory_break",
			args: { duration, is_of_legal_age: frm.doc.is_of_legal_age },
			callback: (response) => frm.set_value("mandatory_break", response.message || 0),
		});
	} else {
		frm.set_value("mandatory_break", 0);
	}
}

function set_break_time(frm) {
	const break_time = frm.doc.indicated_break || frm.doc.mandatory_break;
	frm.set_value("break_time", break_time);
}

function set_working_time(frm, duration) {
	if (frm.doc.check_in && frm.doc.check_out) {
		frm.set_value("working_time", duration - frm.doc.break_time);
	} else {
		frm.set_value("working_time", 0);
	}
}

function update_unallocated_time(frm) {
	const total_duration = frm.doc.time_logs.reduce((sum, row) => sum + row.duration, 0);
	const unallocated_time = frm.doc.working_time - total_duration;
	frm.set_value("unallocated_time", unallocated_time);
}
