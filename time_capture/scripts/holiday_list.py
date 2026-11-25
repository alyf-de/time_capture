import frappe
from frappe import _
from frappe.utils import add_days, getdate, today
from hrms.utils.holiday_list import get_holiday_list_for_employee


def validate(doc, method=None):
	"""Holiday List: validate that a changed period still covers all Attendances of affected Employees."""
	if not doc.is_new() and (doc.has_value_changed("from_date") or doc.has_value_changed("to_date")):
		validate_period(doc.name, doc.from_date, doc.to_date)


def validate_period(holiday_list: str, from_date: str, to_date: str):
	"""Validate Holiday List period for all Employees that are assigned this Holiday List."""
	for employee in _get_employees_with_holiday_list(holiday_list):
		validate_holiday_list_periods_for_employee(
			employee,
			holiday_list=holiday_list,
			holiday_list_dates={holiday_list: (getdate(from_date), getdate(to_date))},
		)


def get_holiday_list(employee: str, date=None) -> str | None:
	"""Return the Holiday List assigned to an Employee (or their Company) on the given date."""
	return get_holiday_list_for_employee(employee, raise_exception=False, as_on=getdate(date))


def warn_if_no_active_holiday_list(employee: str, company: str | None = None):
	"""Show a message if neither the Employee nor their Company has an active Holiday List Assignment."""
	if get_holiday_list(employee, today()):
		return

	frappe.msgprint(
		_(
			"There is currently no active Holiday List Assignment for Employee {0} or their Company {1}. Time Capture needs it to determine holidays and expected working hours. Please create a {2}."
		).format(
			frappe.bold(employee),
			frappe.bold(company or frappe.db.get_value("Employee", employee, "company")),
			f'<a href="/app/holiday-list-assignment/new">{_("Holiday List Assignment")}</a>',
		),
		title=_("Holiday List Assignment missing"),
		indicator="orange",
	)


def get_holiday_list_periods(employee: str) -> list[frappe._dict]:
	"""Return the periods in which a Holiday List applies to an Employee.

	Mirrors the resolution in `hrms.utils.holiday_list.get_holiday_list_for_employee`:
	the latest Employee assignment wins; Company assignments only apply before the
	Employee's first own assignment.

	Each period has `name` (of the assignment), `holiday_list`, `from_date` and `to_date`
	(`to_date` is None for the latest, open-ended period).
	"""
	company = frappe.db.get_value("Employee", employee, "company")
	employee_assignments = _get_assignments("Employee", employee)
	company_assignments = _get_assignments("Company", company) if company else []

	if employee_assignments:
		first_employee_assignment = employee_assignments[0].from_date
		company_assignments = [a for a in company_assignments if a.from_date < first_employee_assignment]

	assignments = company_assignments + employee_assignments
	for i, current in enumerate(assignments):
		following = assignments[i + 1] if i + 1 < len(assignments) else None
		current.to_date = add_days(following.from_date, -1) if following else None

	return assignments


def validate_holiday_list_periods_for_employee(
	employee: str,
	holiday_list: str | None = None,
	assignment: str | None = None,
	holiday_list_dates: dict | None = None,
):
	"""Validate that all submitted Attendances of an Employee lie within the Holiday List assigned for their date.

	:param holiday_list: only check periods that use this Holiday List.
	:param assignment: only check the period of this Holiday List Assignment.
	:param holiday_list_dates: override the (from_date, to_date) of Holiday Lists that are being changed.
	"""
	holiday_list_dates = holiday_list_dates or {}

	for period in get_holiday_list_periods(employee):
		if holiday_list and period.holiday_list != holiday_list:
			continue
		if assignment and period.name != assignment:
			continue

		min_attendance_date, max_attendance_date = _get_attendance_span(
			employee, period.from_date, period.to_date
		)
		if not min_attendance_date:
			continue

		hl_from_date, hl_to_date = holiday_list_dates.get(period.holiday_list) or frappe.db.get_value(
			"Holiday List", period.holiday_list, ["from_date", "to_date"]
		)
		if getdate(hl_from_date) <= min_attendance_date and getdate(hl_to_date) >= max_attendance_date:
			continue

		msg = _("Employee {0} has Attendances outside the period of Holiday List {1}.").format(
			employee, period.holiday_list
		)
		msg += "<br>" + _(
			"Please adjust the Holiday List or its Holiday List Assignment, such that it covers all Attendances (from {0} to {1} and possibly ongoing)."
		).format(frappe.utils.format_date(min_attendance_date), frappe.utils.format_date(max_attendance_date))
		frappe.throw(msg)


def _get_assignments(applicable_for: str, assigned_to: str) -> list[frappe._dict]:
	return frappe.get_all(
		"Holiday List Assignment",
		filters={"applicable_for": applicable_for, "assigned_to": assigned_to, "docstatus": 1},
		fields=["name", "holiday_list", "from_date"],
		order_by="from_date asc",
	)


def _get_employees_with_holiday_list(holiday_list: str) -> list[str]:
	assignments = frappe.get_all(
		"Holiday List Assignment",
		filters={"holiday_list": holiday_list, "docstatus": 1},
		fields=["applicable_for", "assigned_to"],
		distinct=True,
	)
	employees = {a.assigned_to for a in assignments if a.applicable_for == "Employee"}
	companies = {a.assigned_to for a in assignments if a.applicable_for == "Company"}
	if companies:
		employees.update(frappe.get_all("Employee", filters={"company": ("in", companies)}, pluck="name"))

	return sorted(employees)


def _get_attendance_span(employee: str, from_date, to_date):
	filters = [
		["employee", "=", employee],
		["docstatus", "=", 1],
		["attendance_date", ">=", from_date],
	]
	if to_date:
		filters.append(["attendance_date", "<=", to_date])

	span = frappe.get_all(
		"Attendance",
		filters=filters,
		fields=[
			{"MIN": "attendance_date", "as": "min_attendance_date"},
			{"MAX": "attendance_date", "as": "max_attendance_date"},
		],
	)
	if not span:
		return None, None

	return span[0].min_attendance_date, span[0].max_attendance_date
