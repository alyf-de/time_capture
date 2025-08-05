# TODO: Make this available via button.
# INPUT: Number of Days (Urlaubstage), Language, ...

master_configuration = {
	"Leave Type": [
		{
			"leave_type_name": "Annual Leave",
			"is_carry_forward": 1,
		},
		{
			"leave_type_name": "Sick Leave",
			# TODO: Allow Negative Balance: 1
		},
		{
			"leave_type_name": "Overtime Compensation",
			"is_compensatory": 1,
			# TODO: Allow Negative Balance: 1
		},
	],
	"Leave Policy": [
		{
			"title": "30 Days (Standard)",
			"leave_policy_details": [
				{
					"leave_type": "Annual Leave",
					"annual_allocation": 30,
				},
				{
					"leave_type": "Sick Leave",
					"annual_allocation": 360,
				},
				{
					"leave_type": "Overtime Compensation",
					"annual_allocation": 360,
				},
			],
		}
	],
	# TODO: Automatically create a Holiday List.
}

test_records = {
	"Holiday List": [
		{
			"holiday_list_name": "Standard Holiday List",
			"holidays": [
				# Major Holidays 2025
				{
					"holiday_date": "2025-01-01",
					"description": "New Year's Day",
				},
				{
					"holiday_date": "2025-01-06",
					"description": "Epiphany",
				},
				{
					"holiday_date": "2025-04-18",
					"description": "Good Friday",
				},
				{
					"holiday_date": "2025-04-20",
					"description": "Easter Sunday",
				},
				{
					"holiday_date": "2025-04-21",
					"description": "Easter Monday",
				},
				{
					"holiday_date": "2025-05-01",
					"description": "Labor Day",
				},
				{
					"holiday_date": "2025-05-29",
					"description": "Ascension Day",
				},
				{
					"holiday_date": "2025-06-08",
					"description": "Whit Sunday",
				},
				{
					"holiday_date": "2025-06-09",
					"description": "Whit Monday",
				},
				{
					"holiday_date": "2025-10-03",
					"description": "German Unity Day",
				},
				{
					"holiday_date": "2025-12-25",
					"description": "Christmas Day",
				},
				{
					"holiday_date": "2025-12-26",
					"description": "Boxing Day",
				},
				# All Saturdays 2025
				{"holiday_date": "2025-01-04", "description": "Saturday"},
				{"holiday_date": "2025-01-11", "description": "Saturday"},
				{"holiday_date": "2025-01-18", "description": "Saturday"},
				{"holiday_date": "2025-01-25", "description": "Saturday"},
				{"holiday_date": "2025-02-01", "description": "Saturday"},
				{"holiday_date": "2025-02-08", "description": "Saturday"},
				{"holiday_date": "2025-02-15", "description": "Saturday"},
				{"holiday_date": "2025-02-22", "description": "Saturday"},
				{"holiday_date": "2025-03-01", "description": "Saturday"},
				{"holiday_date": "2025-03-08", "description": "Saturday"},
				{"holiday_date": "2025-03-15", "description": "Saturday"},
				{"holiday_date": "2025-03-22", "description": "Saturday"},
				{"holiday_date": "2025-03-29", "description": "Saturday"},
				{"holiday_date": "2025-04-05", "description": "Saturday"},
				{"holiday_date": "2025-04-12", "description": "Saturday"},
				{"holiday_date": "2025-04-26", "description": "Saturday"},
				{"holiday_date": "2025-05-03", "description": "Saturday"},
				{"holiday_date": "2025-05-10", "description": "Saturday"},
				{"holiday_date": "2025-05-17", "description": "Saturday"},
				{"holiday_date": "2025-05-24", "description": "Saturday"},
				{"holiday_date": "2025-05-31", "description": "Saturday"},
				{"holiday_date": "2025-06-07", "description": "Saturday"},
				{"holiday_date": "2025-06-14", "description": "Saturday"},
				{"holiday_date": "2025-06-21", "description": "Saturday"},
				{"holiday_date": "2025-06-28", "description": "Saturday"},
				{"holiday_date": "2025-07-05", "description": "Saturday"},
				{"holiday_date": "2025-07-12", "description": "Saturday"},
				{"holiday_date": "2025-07-19", "description": "Saturday"},
				{"holiday_date": "2025-07-26", "description": "Saturday"},
				{"holiday_date": "2025-08-02", "description": "Saturday"},
				{"holiday_date": "2025-08-09", "description": "Saturday"},
				{"holiday_date": "2025-08-16", "description": "Saturday"},
				{"holiday_date": "2025-08-23", "description": "Saturday"},
				{"holiday_date": "2025-08-30", "description": "Saturday"},
				{"holiday_date": "2025-09-06", "description": "Saturday"},
				{"holiday_date": "2025-09-13", "description": "Saturday"},
				{"holiday_date": "2025-09-20", "description": "Saturday"},
				{"holiday_date": "2025-09-27", "description": "Saturday"},
				{"holiday_date": "2025-10-04", "description": "Saturday"},
				{"holiday_date": "2025-10-11", "description": "Saturday"},
				{"holiday_date": "2025-10-18", "description": "Saturday"},
				{"holiday_date": "2025-10-25", "description": "Saturday"},
				{"holiday_date": "2025-11-01", "description": "Saturday"},
				{"holiday_date": "2025-11-08", "description": "Saturday"},
				{"holiday_date": "2025-11-15", "description": "Saturday"},
				{"holiday_date": "2025-11-22", "description": "Saturday"},
				{"holiday_date": "2025-11-29", "description": "Saturday"},
				{"holiday_date": "2025-12-06", "description": "Saturday"},
				{"holiday_date": "2025-12-13", "description": "Saturday"},
				{"holiday_date": "2025-12-20", "description": "Saturday"},
				{"holiday_date": "2025-12-27", "description": "Saturday"},
				# All Sundays 2025
				{"holiday_date": "2025-01-05", "description": "Sunday"},
				{"holiday_date": "2025-01-12", "description": "Sunday"},
				{"holiday_date": "2025-01-19", "description": "Sunday"},
				{"holiday_date": "2025-01-26", "description": "Sunday"},
				{"holiday_date": "2025-02-02", "description": "Sunday"},
				{"holiday_date": "2025-02-09", "description": "Sunday"},
				{"holiday_date": "2025-02-16", "description": "Sunday"},
				{"holiday_date": "2025-02-23", "description": "Sunday"},
				{"holiday_date": "2025-03-02", "description": "Sunday"},
				{"holiday_date": "2025-03-09", "description": "Sunday"},
				{"holiday_date": "2025-03-16", "description": "Sunday"},
				{"holiday_date": "2025-03-23", "description": "Sunday"},
				{"holiday_date": "2025-03-30", "description": "Sunday"},
				{"holiday_date": "2025-04-06", "description": "Sunday"},
				{"holiday_date": "2025-04-13", "description": "Sunday"},
				{"holiday_date": "2025-04-27", "description": "Sunday"},
				{"holiday_date": "2025-05-04", "description": "Sunday"},
				{"holiday_date": "2025-05-11", "description": "Sunday"},
				{"holiday_date": "2025-05-18", "description": "Sunday"},
				{"holiday_date": "2025-05-25", "description": "Sunday"},
				{"holiday_date": "2025-06-01", "description": "Sunday"},
				{"holiday_date": "2025-06-15", "description": "Sunday"},
				{"holiday_date": "2025-06-22", "description": "Sunday"},
				{"holiday_date": "2025-06-29", "description": "Sunday"},
				{"holiday_date": "2025-07-06", "description": "Sunday"},
				{"holiday_date": "2025-07-13", "description": "Sunday"},
				{"holiday_date": "2025-07-20", "description": "Sunday"},
				{"holiday_date": "2025-07-27", "description": "Sunday"},
				{"holiday_date": "2025-08-03", "description": "Sunday"},
				{"holiday_date": "2025-08-10", "description": "Sunday"},
				{"holiday_date": "2025-08-17", "description": "Sunday"},
				{"holiday_date": "2025-08-24", "description": "Sunday"},
				{"holiday_date": "2025-08-31", "description": "Sunday"},
				{"holiday_date": "2025-09-07", "description": "Sunday"},
				{"holiday_date": "2025-09-14", "description": "Sunday"},
				{"holiday_date": "2025-09-21", "description": "Sunday"},
				{"holiday_date": "2025-09-28", "description": "Sunday"},
				{"holiday_date": "2025-10-05", "description": "Sunday"},
				{"holiday_date": "2025-10-12", "description": "Sunday"},
				{"holiday_date": "2025-10-19", "description": "Sunday"},
				{"holiday_date": "2025-10-26", "description": "Sunday"},
				{"holiday_date": "2025-11-02", "description": "Sunday"},
				{"holiday_date": "2025-11-09", "description": "Sunday"},
				{"holiday_date": "2025-11-16", "description": "Sunday"},
				{"holiday_date": "2025-11-23", "description": "Sunday"},
				{"holiday_date": "2025-11-30", "description": "Sunday"},
				{"holiday_date": "2025-12-07", "description": "Sunday"},
				{"holiday_date": "2025-12-14", "description": "Sunday"},
				{"holiday_date": "2025-12-21", "description": "Sunday"},
				{"holiday_date": "2025-12-28", "description": "Sunday"},
			],
		},
	],
	"Employee": [
		{
			"employee_name": "John Doe",
			"employee_number": "EMP001",
			"gender": "Male",
			"date_of_birth": "1990-01-01",
			"date_of_joining": "2025-01-01",
			"leave_policy": "30 Days (Standard)",
			"holiday_list": "Standard Holiday List",
		},
		{
			"employee_name": "Jane Smith",
			"employee_number": "EMP002",
			"gender": "Female",
			"date_of_birth": "1992-05-15",
			"date_of_joining": "2025-01-01",
			"leave_policy": "30 Days (Standard)",
			"holiday_list": "Standard Holiday List",
		},
	],
	"Leave Policy Assignment": [
		{
			"employee": "John Doe",
			"leave_policy": "30 Days (Standard)",
		},
		{
			"employee": "Jane Smith",
			"leave_policy": "30 Days (Standard)",
		},
	],
}
