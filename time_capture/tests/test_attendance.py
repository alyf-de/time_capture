import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate

from time_capture.scripts.attendance import _calculate_attendance_metrics
from time_capture.scripts.employee import get_expected_working_hours
from time_capture.tests.attendance_records import master_configuration, test_records


class TestAttendanceCalculations(FrappeTestCase):
	def setUp(self):
		"""Set up test data for attendance calculations"""
		self.create_test_data()

	def tearDown(self):
		"""Clean up test data"""
		self.cleanup_test_data()

	def create_test_data(self):
		"""Create all necessary test data"""
		self.create_leave_types()
		self.create_leave_policies()
		self.create_holiday_lists()
		self.create_employees()
		self.create_leave_policy_assignments()
		self.create_expected_working_hours()

	def create_leave_types(self):
		"""Create leave types from master configuration"""
		for leave_type_data in master_configuration["Leave Type"]:
			if not frappe.db.exists("Leave Type", leave_type_data["leave_type_name"]):
				leave_type = frappe.get_doc({"doctype": "Leave Type", **leave_type_data})
				leave_type.insert()

	def create_leave_policies(self):
		"""Create leave policies from master configuration"""
		for policy_data in master_configuration["Leave Policy"]:
			if not frappe.db.exists("Leave Policy", policy_data["title"]):
				policy = frappe.get_doc(
					{
						"doctype": "Leave Policy",
						"title": policy_data["title"],
					}
				)

				for detail in policy_data["leave_policy_details"]:
					policy.append(
						"leave_policy_details",
						{
							"leave_type": detail["leave_type"],
							"annual_allocation": detail["annual_allocation"],
						},
					)

				policy.insert()

	def create_holiday_lists(self):
		"""Create holiday lists from test records"""
		for holiday_list_data in test_records["Holiday List"]:
			if not frappe.db.exists("Holiday List", holiday_list_data["holiday_list_name"]):
				holiday_list = frappe.get_doc(
					{
						"doctype": "Holiday List",
						"holiday_list_name": holiday_list_data["holiday_list_name"],
						"from_date": "2025-01-01",
						"to_date": "2025-12-31",
						"holidays": [],
					}
				)

				for holiday_data in holiday_list_data["holidays"]:
					holiday_list.append("holidays", holiday_data)

				holiday_list.insert()

	def create_employees(self):
		"""Create employees from test records"""
		for employee_data in test_records["Employee"]:
			if not frappe.db.exists("Employee", employee_data["employee_name"]):
				employee = frappe.get_doc({"doctype": "Employee", **employee_data})
				employee.insert()

	def create_leave_policy_assignments(self):
		"""Create leave policy assignments from test records"""
		for assignment_data in test_records["Leave Policy Assignment"]:
			if not frappe.db.exists(
				"Leave Policy Assignment",
				{"employee": assignment_data["employee"], "leave_policy": assignment_data["leave_policy"]},
			):
				assignment = frappe.get_doc({"doctype": "Leave Policy Assignment", **assignment_data})
				assignment.insert()

	def create_expected_working_hours(self):
		"""Create expected working hours for employees"""
		employees = frappe.get_all("Employee", pluck="name")
		for employee in employees:
			# Check if expected working hours already exist
			existing = frappe.get_all(
				"Employee Expected Working Hours", filters={"parent": employee}, pluck="name"
			)

			if not existing:
				employee_doc = frappe.get_doc("Employee", employee)
				employee_doc.append(
					"expected_working_hours",
					{"valid_from": employee_doc.date_of_joining, "expected_daily_working_hours": 8.0},
				)
				employee_doc.save()

	def cleanup_test_data(self):
		"""Clean up all test data"""
		# Clean up in reverse order of creation
		frappe.db.sql("DELETE FROM `tabLeave Policy Assignment` WHERE employee IN ('John Doe', 'Jane Smith')")
		frappe.db.sql(
			"DELETE FROM `tabEmployee Expected Working Hours` WHERE parent IN ('John Doe', 'Jane Smith')"
		)
		frappe.db.sql("DELETE FROM `tabEmployee` WHERE employee_name IN ('John Doe', 'Jane Smith')")
		frappe.db.sql("DELETE FROM `tabHoliday` WHERE parent = 'Standard Holiday List'")
		frappe.db.sql("DELETE FROM `tabHoliday List` WHERE holiday_list_name = 'Standard Holiday List'")
		frappe.db.sql("DELETE FROM `tabLeave Policy Detail` WHERE parent = '30 Days (Standard)'")
		frappe.db.sql("DELETE FROM `tabLeave Policy` WHERE title = '30 Days (Standard)'")
		frappe.db.sql(
			"DELETE FROM `tabLeave Type` WHERE leave_type_name IN ('Annual Leave', 'Sick Leave', 'Overtime Compensation')"
		)
		frappe.db.commit()

	def test_attendance_calculations(self):
		"""Test attendance calculations with the setup data"""
		# This test will be implemented with actual test cases
		pass

	def test_data_setup(self):
		"""Test that all test data was created successfully"""
		# Test that leave types were created
		self.assertTrue(frappe.db.exists("Leave Type", "Annual Leave"))
		self.assertTrue(frappe.db.exists("Leave Type", "Sick Leave"))
		self.assertTrue(frappe.db.exists("Leave Type", "Overtime Compensation"))

		# Test that leave policy was created
		self.assertTrue(frappe.db.exists("Leave Policy", "30 Days (Standard)"))

		# Test that holiday list was created
		self.assertTrue(frappe.db.exists("Holiday List", "Standard Holiday List"))

		# Test that employees were created
		self.assertTrue(frappe.db.exists("Employee", "John Doe"))
		self.assertTrue(frappe.db.exists("Employee", "Jane Smith"))

		# Test that leave policy assignments were created
		assignments = frappe.get_all(
			"Leave Policy Assignment", filters={"employee": ["in", ["John Doe", "Jane Smith"]]}
		)
		self.assertEqual(len(assignments), 2)

		# Test that expected working hours were created
		expected_hours = frappe.get_all(
			"Employee Expected Working Hours", filters={"parent": ["in", ["John Doe", "Jane Smith"]]}
		)
		self.assertEqual(len(expected_hours), 2)

		# Test that holidays were created
		holidays = frappe.get_all("Holiday", filters={"parent": "Standard Holiday List"})
		self.assertGreater(len(holidays), 100)  # Should have many holidays for 2025

	def test_attendance_calculation_with_setup_data(self):
		"""Test attendance calculations using the setup data"""
		# Create an attendance record for John Doe on a working day
		attendance = frappe.get_doc(
			{
				"doctype": "Attendance",
				"employee": "John Doe",
				"attendance_date": "2025-01-02",  # Thursday, working day
				"working_hours": 8.0,
				"status": "Present",
			}
		)
		attendance.insert()

		# Test the attendance metrics calculation
		working_hours, expected_working_hours, flexitime = _calculate_attendance_metrics(attendance)

		# Verify the calculations
		self.assertEqual(working_hours, 8.0)
		self.assertEqual(expected_working_hours, 8.0)  # From expected working hours
		self.assertEqual(flexitime, 0.0)  # No overtime or undertime

		# Test expected working hours function
		expected_hours = get_expected_working_hours("John Doe", "2025-01-02")
		self.assertEqual(expected_hours, 8.0)

		# Clean up
		attendance.delete()

	def test_attendance_on_holiday(self):
		"""Test attendance on a holiday (should have 0 expected working hours)"""
		# New Year's Day is a holiday
		expected_hours = get_expected_working_hours("John Doe", "2025-01-01")
		self.assertEqual(expected_hours, 0.0)

		# Create attendance on holiday
		attendance = frappe.get_doc(
			{
				"doctype": "Attendance",
				"employee": "John Doe",
				"attendance_date": "2025-01-01",  # New Year's Day
				"working_hours": 0.0,
				"status": "Absent",
			}
		)
		attendance.insert()

		# Test the attendance metrics calculation
		working_hours, expected_working_hours, flexitime = _calculate_attendance_metrics(attendance)

		# Verify the calculations
		self.assertEqual(working_hours, 0.0)
		self.assertEqual(expected_working_hours, 0.0)  # Holiday
		self.assertEqual(flexitime, 0.0)

		# Clean up
		attendance.delete()
