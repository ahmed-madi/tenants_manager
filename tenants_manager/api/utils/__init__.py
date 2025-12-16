import frappe
from tenants_manager.api.utils.response import build_error_response

owner_doc_order_status = [
    "New",
    "Owner Info Completed",
    # "Password Added",
    "Email Verified",
    "Phone Number Added",
    "Phone Number Verified",
    "Business Info Completed",
    "Business Address Completed",
    "Completed",
]

business_doc_order_status = [
    "New",
    "Business Name Added",
    "Logo Added",
    "Atmosphere Keywords Added",
    "Specialties Keywords Added",
    "Completed",
]


def get_owner_next_status_step(current):
    if current == "New":
        return "Owner Info"
    elif current == "Owner Info Completed":
        return "Email Verification"
    # elif current == "Password Added":
    #     return "Email Verification"
    elif current == "Email Verified":
        return "Phone Number"
    elif current == "Phone Number Added":
        return "Phone Number Verification"
    elif current == "Phone Number Verified":
        return "Business Info"
    elif current == "Business Info Completed":
        return "Business Address"
    elif current == "Business Address Completed":
        return "Completed"
    return "Completed"


def get_business_next_status_step(current):
    if current == "New":
        return "Business Name"
    elif current == "Business Name Added":
        return "Upload Logo"
    elif current == "Logo Added":
        return "Add Atmosphere Keywords"
    elif current == "Atmosphere Keywords Added":
        return "Add Specialties Keywords"
    elif current == "Specialties Keywords Added":
        return "Completed"
    return "Completed"


def is_doc_status_valid_to_update(
    doc_status, status, source_id, doctype="Business Owner"
):
    order_status = owner_doc_order_status
    call_func = get_owner_next_status_step
    if doctype == "Business":
        order_status = business_doc_order_status
        call_func = get_business_next_status_step

    doc_status_idx = order_status.index(doc_status)
    status_idx = order_status.index(status)

    if doc_status_idx >= status_idx - 1:
        return True
    build_error_response(
        "CONFLICT",
        {
            "resource_type": doctype,
            "resource_id": source_id or "",
            "current_status": frappe.scrub(doc_status).replace("_", "-"),
            "next_step": frappe.scrub(call_func(doc_status)).replace("_", "-"),
        },
        409,
        "The resource could not be updated Due to conflict of the status",
    )
    return False


def is_doc_status_after_current(doc_status, status, doctype="Business Owner"):
    order_status = owner_doc_order_status
    if doctype == "Business":
        order_status = business_doc_order_status

    doc_status_idx = order_status.index(doc_status)
    status_idx = order_status.index(status)
    return doc_status_idx > status_idx


def check_business_owner(source_id):
    name = (
        frappe.get_value(
            "Business Owner",
            {"name": source_id},
            "name",
        )
        or None
    )
    if not name:
        build_error_response(
            "NOT_FOUND",
            {"resource_type": "Business Owner", "resource_id": source_id or ""},
            404,
            # "The requested resource could not be found or dose not match with email",
            "The requested Business Owner could not be found",
        )
    return name


def check_business(source_id):
    name = (
        frappe.get_value(
            "Business",
            {"name": source_id},
            "name",
        )
        or None
    )
    if not name:
        build_error_response(
            "NOT_FOUND",
            {"resource_type": "Business", "resource_id": source_id or ""},
            404,
            # "The requested resource could not be found or dose not match with email",
            "The requested Business could not be found",
        )
    return name


def check_existence(doctype: str, doc_id: str):
    name = (
        frappe.get_value(
            doctype,
            {"name": doc_id},
            "name",
        )
        or None
    )
    if not name:
        build_error_response(
            "NOT_FOUND",
            {"resource_type": doctype, "resource_id": doc_id or ""},
            404,
            # "The requested resource could not be found or dose not match with email",
            f"The requested {doctype} could not be found",
        )
    return name