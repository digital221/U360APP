import frappe
from datetime import datetime
from frappe.utils import cstr, cint, flt, getdate
from unify360.flutter_apis.main import create_log, make_response, get_user_details
from json import loads


@frappe.whitelist()
def get_attendance():
    try:
        data = []
        user_details = get_user_details()
        if user_details:
            data = frappe.db.sql(
                f""" select employee, employee_name, working_hours, attendance_date, out_time, in_time from `tabAttendance` 
                WHERE employee = '{user_details.get("employee")}' """,
                as_dict=1,
            ) or []
            count_data = frappe.db.sql(
                f""" SELECT status, COUNT(name) as data_count FROM `tabAttendance` WHERE employee = '{user_details.get("employee")}' 
                GROUP BY status
                """,
                as_dict=1,
            ) or []
            for row in data:
                if not row.get("in_time"):
                    row["in_time"] = "00:00:00"

                if not row.get("out_time"):
                    row["out_time"] = "00:00:00"

        graph_data = {
            "Work From Home": 0,
            "Half Day": 0,
            "On Leave": 0,
            "Absent": 0,
            "Present": 0,
        }
        for abc in count_data:
            graph_data[abc.status] = flt(abc.data_count)

        frappe.response["graph"] = graph_data
        frappe.response["data"] = data
        return
        # make_response(success=True, data=data)
    except Exception as e:
        make_response(success=False, message=str(e))


@frappe.whitelist(allow_guest=True)
def add_leaves():
    user_details = get_user_details()
    data: dict = loads(frappe.request.data)

    if user_details:
        leave_doc = frappe.new_doc("Leave Application")
        leave_doc.employee = user_details.get("employee")
        leave_doc.leave_type = data.get("leave_type")
        leave_doc.description = data.get("reason")
        leave_doc.from_date = datetime.strptime(data.get("from_date"), "%Y-%m-%d")
        leave_doc.to_date = datetime.strptime(data.get("to_date"), "%Y-%m-%d")

        if data.get("half_day"):
            leave_doc.half_day = bool(data.get("half_day"))
        leave_doc.save(ignore_permissions=True)

        frappe.db.commit()

        frappe.response["message"] = "Leave added successfully!"
        frappe.response["data"] = leave_doc
    else:
        frappe.response["message"] = "session user not found!"


@frappe.whitelist(allow_guest=True)
def add_attendence():
    try:
        data = loads(frappe.request.data)
        if data:
            user_details = get_user_details()
            doc = frappe.new_doc("Employee Checkin")
            doc.employee = user_details.get("employee")
            doc.log_type = data.get("type")
            datetime_str = f"""{data.get('date')} {data.get('time')}"""
            datetime_str = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            doc.time = datetime_str
            doc.save(ignore_permissions=True)
            frappe.response["message"] = "Attendance added"
        else:
            frappe.response["message"] = "Data not found"
    except Exception as e:
        create_log("Api Failed", e)
