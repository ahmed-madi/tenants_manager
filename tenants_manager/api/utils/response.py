import frappe
from frappe.utils import now
from tenants_manager.validators.messages import get_message


def build_response(data, message, status_code=200):
    response = {
        "status": "success",
        "data": data,
        "message": message,
        "timestamp": f"{now()}",
    }
    frappe.local.response.http_status_code = status_code
    frappe.local.response.update(response)


def build_error_response(error_code, details, status_code=500, message=None):
    error = get_message(error_code, details, now(), message)
    error_status_code = error.pop("status_code", None)
    if error_status_code:
        status_code = error_status_code
    frappe.local.response.http_status_code = status_code
    frappe.local.response.update(error)
