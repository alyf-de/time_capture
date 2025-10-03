// Copyright (c) 2024, Time Capture and contributors
// For license information, please see license.txt

frappe.provide("time_capture.utils");

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
			fieldname: ["name"],
		},
		callback: function (r) {
			if (r.message && r.message.name) {
				time_capture.utils.show_leave_and_time_summary_for_employee(r.message);
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

time_capture.utils.show_leave_and_time_summary_for_employee = function (employee) {
	// Call both functions in parallel to avoid duplicate calls
	let leave_call = frappe.call({
		method: "hrms.hr.doctype.leave_application.leave_application.get_leave_details",
		args: {
			employee: employee.name,
			date: frappe.datetime.get_today(),
		},
	});

	let time_call = frappe.call({
		method: "time_capture.scripts.summary_utils.get_working_time_summary_for_employee",
		args: {
			employee: employee.name,
		},
	});

	// Handle both calls with Promise.all-like behavior
	let leave_data = null;
	let time_data = null;
	let leave_error = null;
	let time_error = null;
	let completed_calls = 0;

	function check_completion() {
		completed_calls++;
		if (completed_calls === 2) {
			// Both calls completed, show dialog with available data
			show_summary_dialog(leave_data, time_data, leave_error, time_error, employee);
		}
	}

	// Handle leave details call
	leave_call
		.then(function (r) {
			leave_data = {
				leave_allocation: r.message["leave_allocation"] || {},
				lwps: r.message["lwps"] || [],
			};
			check_completion();
		})
		.catch(function (err) {
			leave_error = err;
			check_completion();
		});

	// Handle time summary call
	time_call
		.then(function (r) {
			time_data = r.message || {};
			check_completion();
		})
		.catch(function (err) {
			time_error = err;
			check_completion();
		});
};

function show_summary_dialog(leave_data, time_data, leave_error, time_error, employee) {
	let dialog_title = __("Summary");
	let leave_details = {};
	let lwps = [];
	let time_summary = {};

	// Process leave data if available
	if (leave_data && !leave_error) {
		leave_details = leave_data.leave_allocation;
		lwps = leave_data.lwps;
	}

	// Process time data if available
	if (time_data && !time_error) {
		time_summary = time_data;
	}

	// Determine dialog title based on available data
	if (leave_error && time_error) {
		dialog_title = __("Error");
	} else if (leave_error) {
		dialog_title = __("Time Capture Summary");
	} else if (time_error) {
		dialog_title = __("Leave Summary");
	}

	// Show error if both calls failed
	if (leave_error && time_error) {
		frappe.msgprint({
			title: __("Error"),
			message: __("Unable to fetch summary data"),
			indicator: "red",
		});
		return;
	}

	// Create and show dialog
	let dialog = new frappe.ui.Dialog({
		title: dialog_title,
		size: "large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "summary_html",
				options: create_summary_html(leave_details, lwps, time_summary, employee),
			},
		],
	});

	dialog.show();
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

	html += `
			<tr>
				<td style="width: 65%">
					${__("Last Manual Balance Correction")}
					<p style="font-size: 80%; !important">
						${__(
							"This could be (for example) a starting balance you took on from your previous time capture system."
						)}
					</p>
				</td>
				<td style="width: 35%">${time_summary.flexitime_correction}</td>
			</tr>
			<tr">
				<td>
					${__("Current Balance")}
					<p style="font-size: 80%; !important">
						${__(
							"This includes the last manual balance correction (if existing) and the sum of your working hours (minus your expected working hours)."
						)}
					</p>
				</td>
				<td>${time_summary.current_balance || 0}</td>
			</tr>
			<tr>
				<td>
					${__("Planned Overtime Reduction")}
					<p style="font-size: 80%; !important">
						${__("Future, approved overtime reductions.")}
					</p>
				</td>
				<td>${time_summary.future_balance_changes || 0}</td>
			</tr>
			<tr>
				<td>
					${__("Future Balance (after planned reduction)")}
					<p style="font-size: 80%; !important">
						${__("This is the projected balance, that includes planned overtime reductions")}
					</p>
				</td>
				<td>${time_summary.future_balance || 0}</td>
			</tr>
			<tr>
				<td>
					${__("Overdue Time Captures")}
					<p style="font-size: 80%; !important">
						${__(
							"Past time captures, that are not yet submitted. These count as absent and reduce the balance."
						)}
					</p>
				</td>
				<td>${time_summary.open_time_captures || 0}</td>
			</tr>
		`;

	// Only show "No working time data found" if there's no data
	if (
		!time_summary ||
		Object.keys(time_summary).length === 0 ||
		(!time_summary.flexitime_correction &&
			!time_summary.current_balance &&
			!time_summary.future_balance_changes &&
			!time_summary.future_balance &&
			!time_summary.open_time_captures)
	) {
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
