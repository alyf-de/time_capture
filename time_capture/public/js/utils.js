// Copyright (c) 2024, Time Capture and contributors
// For license information, please see license.txt

// Define the function in global scope
frappe.ui.toolbar.show_time_capture_and_leave_summary = function () {
	// Get current employee by user_id
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Employee",
			filters: {
				user_id: frappe.session.user,
			},
			fieldname: ["name", "employee_name", "company"],
		},
		callback: function (r) {
			if (r.message && r.message.name) {
				show_leave_and_time_summary(r.message);
			} else {
				frappe.msgprint({
					title: __("Error"),
					message: __("No employee found for current user"),
					indicator: "red",
				});
			}
		},
	});
};

function show_leave_and_time_summary(employee) {
	// Get leave details
	frappe.call({
		method: "hrms.hr.doctype.leave_application.leave_application.get_leave_details",
		args: {
			employee: employee.name,
			date: frappe.datetime.get_today(),
		},
		callback: function (r) {
			let leave_details = r.message["leave_allocation"] || {};
			let lwps = r.message["lwps"] || [];

			// Get working time summary details
			frappe.call({
				method: "time_capture.scripts.summary_utils.get_working_time_summary_for_employee",
				args: {
					employee: employee.name,
				},
				callback: function (time_r) {
					let time_summary = time_r.message || {};

					// Create and show dialog
					let dialog = new frappe.ui.Dialog({
						title: __("Time Capture & Leave Summary"),
						size: "large",
						fields: [
							{
								fieldtype: "HTML",
								fieldname: "summary_html",
								options: create_summary_html(
									leave_details,
									lwps,
									time_summary,
									employee
								),
							},
						],
					});

					dialog.show();
				},
				error: function (err) {
					// If time capture method fails, show only leave details
					let dialog = new frappe.ui.Dialog({
						title: __("Leave Summary"),
						size: "large",
						fields: [
							{
								fieldtype: "HTML",
								fieldname: "summary_html",
								options: create_summary_html(leave_details, lwps, {}, employee),
							},
						],
					});

					dialog.show();
				},
			});
		},
		error: function (err) {
			// If leave details fail, show only working time summary
			frappe.call({
				method: "time_capture.scripts.summary_utils.get_working_time_summary_for_employee",
				args: {
					employee: employee.name,
				},
				callback: function (time_r) {
					let time_summary = time_r.message || {};

					let dialog = new frappe.ui.Dialog({
						title: __("Time Capture Summary"),
						size: "large",
						fields: [
							{
								fieldtype: "HTML",
								fieldname: "summary_html",
								options: create_summary_html({}, [], time_summary, employee),
							},
						],
					});

					dialog.show();
				},
				error: function (err) {
					frappe.msgprint({
						title: __("Error"),
						message: __("Unable to fetch summary data"),
						indicator: "red",
					});
				},
			});
		},
	});
}

function create_summary_html(leave_details, lwps, time_summary, employee) {
	let html = `
		<div class="row">
			<div class="col-md-12">
				<h4>${__("Leave Summary")}</h4>
				<div class="table-responsive">
					<table class="table table-bordered">
						<thead>
							<tr>
								<th>${__("Leave Type")}</th>
								<th>${__("Allocated")}</th>
								<th>${__("Used")}</th>
								<th>${__("Balance")}</th>
							</tr>
						</thead>
						<tbody>
	`;

	// Add leave details
	Object.keys(leave_details).forEach((leave_type) => {
		let details = leave_details[leave_type];
		html += `
			<tr>
				<td>${leave_type}</td>
				<td>${details.total_leaves || 0}</td>
				<td>${details.leaves_taken || 0}</td>
				<td>${details.remaining_leaves || 0}</td>
			</tr>
		`;
	});

	html += `
						</tbody>
					</table>
				</div>
			</div>
		</div>
		<div class="row" style="margin-top: 20px;">
			<div class="col-md-12">
				<h4>${__("Working Time Summary")}</h4>
				<div class="table-responsive">
					<table class="table table-bordered">
						<tbody>
	`;

	// Add working time details
	if (time_summary && Object.keys(time_summary).length > 0) {
		let correction_date = time_summary.flexitime_correction
			? time_summary.flexitime_correction.date
			: "-";
		let correction_value = time_summary.flexitime_correction
			? time_summary.flexitime_correction.flexitime_hours
			: 0;

		// Format correction display
		let correction_display = "-";
		if (correction_value && correction_date && correction_date !== "-") {
			correction_display = `${correction_value} on ${correction_date}`;
		} else if (correction_value) {
			correction_display = `${correction_value}`;
		} else if (correction_date && correction_date !== "-") {
			correction_display = correction_date;
		}

		html += `
			<tr>
				<td style="width: 65%">${__("Last Manual Correction")}</td>
				<td style="width: 35%">${correction_display}</td>
			</tr>
			<tr>
				<td>${__("Current Balance")}</td>
				<td>${time_summary.current_balance || 0}</td>
			</tr>
			<tr>
				<td>${__("Planned Overtime Reduction (Future)")}</td>
				<td>${time_summary.future_balance_changes || 0}</td>
			</tr>
			<tr>
				<td>${__("Balance after planned overtime reduction")}</td>
				<td>${time_summary.future_balance || 0}</td>
			</tr>
		`;
	} else {
		html += `
			<tr>
				<td colspan="2" class="text-center">${__("No working time data found")}</td>
			</tr>
		`;
	}

	html += `
						</tbody>
					</table>
				</div>
			</div>
		</div>
	`;

	return html;
}
