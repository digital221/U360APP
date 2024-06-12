import frappe
from frappe.utils import cstr, cint, flt, getdate, now
from datetime import datetime


def create_log(title="App Api", message=""):
    frappe.log_error(title, message)


def make_response(success=True, message="Success", data={}, session_success=True):
    frappe.local.response["message"] = {
        "session_success": session_success,
        "success": success,
        "success_key": cint(success),
        "message": message,
        # "data": dumps(data),
        "data": data,
    }

def get_user_details(user=None):
    try:
        if not user:
            user = frappe.session.user
        if user and user not in ["Guest"]:
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
            # sales_person = frappe.db.get_value("Sales Person", {"user": user, "enabled": 1}, "name")
            user = frappe.get_doc("User", user)
            data = {
                "name": user.name,
                "sid": frappe.session.sid,
                "username": user.username,
                "email": user.email,
                "employee": employee,
                # "sales_person": sales_person,
            }
            return frappe._dict(data)
        else:
            make_response(
                success=False, message="Session Not Found.", session_success=False
            )
    except Exception as e:
        create_log("API Test", f"{e}\n{frappe.get_traceback()}")
        make_response(success=False, message="Invalid login credentials!")

def get_date_time_to_use():
    dt = now()
    date, time = dt.split(" ")
    date = date.split("-")
    d = datetime.strptime(time, "%H:%M:%S.%f")
    formatted_time = d.strftime("%I:%M:%S %p")
    time = time.split(":")
    data = {
        "formatted_time": formatted_time,
        "now": dt,
        "today": getdate(),
        "year": date[0],
        "month": date[1],
        "day": date[2],
        "hour": time[0],
        "min": time[1],
        "sec": time[2],
    }
    return frappe._dict(data)

@frappe.whitelist(allow_guest=True)
def get_date_time():
    try:
        user_details = get_user_details()
        if user_details:
            dt = now()
            date, time = dt.split(" ")
            date = date.split("-")
            d = datetime.strptime(time, "%H:%M:%S.%f")
            formatted_time = d.strftime("%I:%M:%S %p")
            time = time.split(":")
            data = {
                "user_details": user_details,
                "formatted_time": formatted_time,
                "now": dt,
                "today": getdate(),
                "year": date[0],
                "month": date[1],
                "day": date[2],
                "hour": time[0],
                "min": time[1],
                "sec": time[2],
            }
            make_response(data=data)
        else:
            make_response(
                success=False, message="Session Not Found.", session_success=False
            )
    except Exception as e:
        create_log("Failed to Send Datetime", e)
        make_response(success=False, message=e)
