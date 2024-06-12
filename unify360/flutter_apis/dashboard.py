import frappe
from datetime import datetime
from frappe.utils import cstr, cint, flt, getdate
from unify360.flutter_apis.main import (
    create_log,
    make_response,
    get_user_details,
    get_date_time_to_use,
)
from unify360.flutter_apis.leave_application_custom import get_leave_details
from json import loads


@frappe.whitelist(allow_guest=True)
def get_dashboard_data():
    try:
        user_details = get_user_details()
        if user_details:
            leaves = {}
            leave_allocation = {}
            leave_data = get_leave_details(user_details.employee, getdate())

            if leave_data:
                leave_allocation = leave_data.get("leave_allocation", {})
                for leave_type, leave_type_data in leave_allocation.items():
                    if leave_type not in leaves:
                        leaves[leave_type] = {
                            "total_leaves": 0,
                            "leaves_used": 0,
                        }
                    if leave_type_data:
                        leaves[leave_type]["total_leaves"] += leave_type_data.get(
                            "total_leaves"
                        )
                        leaves[leave_type]["leaves_used"] += leave_type_data.get(
                            "leaves_taken"
                        )
            dt = get_date_time_to_use()
            month = dt.month
            data_get_dict = {
                "current_task": """ SELECT creation, priority, name as id, actual_time, expected_time, exp_end_date from `tabTask` where  1 = 1  ORDER BY creation desc""",
                "pending_request": f"""SELECT ec.name as id, ec.status,expense_date, ecd.description, ecd.expense_type,ecd.amount from `tabExpense Claim` ec inner join `tabExpense Claim Detail` ecd on ec.name = ecd.parent where ec.docstatus=1 and MONTH(ec.posting_date) = {month} """,
                "salary_details": f"""SELECT MONTHNAME(posting_date) as month_name,total_working_days,gross_pay from `tabSalary Slip` where 1 = 1 and MONTH(posting_date) = {month} """,
            }
            for field, query in data_get_dict.items():
                data = frappe.db.sql(query, as_dict=1)
                data_get_dict[field] = data

            data_get_dict_counts = {
                "attendance_present": f"""SELECT COUNT(name)from `tabAttendance` where status = 'Present' and MONTH(attendance_date) = {month} """,
                "attendance_absent": f"""SELECT COUNT(name) from `tabAttendance` where status = 'Absent' and MONTH(attendance_date) = {month} """,
            }
            for field, query in data_get_dict_counts.items():
                data = frappe.db.sql(query)
                if data:
                    data_get_dict[field] = data[0][0]

            data_get_dict["leave_balance"] = [
                {
                    "leave_type": k,
                    "total_leaves": v.get("total_leaves"),
                    "leaves_used": v.get("leaves_used"),
                }
                for k, v in leaves.items()
            ]

            count_data = (
                frappe.db.sql(
                    f""" SELECT status, COUNT(name) as data_count FROM `tabAttendance` WHERE employee = '{user_details.get("employee")}' 
				GROUP BY status
				""",
                    as_dict=1,
                )
                or []
            )
            graph_data = {
                "Work From Home": 0,
                "Half Day": 0,
                "On Leave": 0,
                "Absent": 0,
                "Present": 0,
            }

            for abc in count_data:
                graph_data[abc.status] = flt(abc.data_count)

            data_get_dict["attendence_graph_data"] = graph_data
            # frappe.response["graph"] = graph_data

            make_response(success=True, data=data_get_dict)
        else:
            make_response(success=False, message="Invalid User!")
    except Exception as e:
        make_response(success=False, message=str(e))
