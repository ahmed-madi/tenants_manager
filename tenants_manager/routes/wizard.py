import frappe

from werkzeug.routing import Rule


def get_status():
    frappe.form_dict.cmd = "tenants_manager.api.subscription.check_email_address"
    return frappe.handler.handle()


def is_email_registered():
    frappe.form_dict.cmd = "tenants_manager.api.subscription.is_email_registered"
    return frappe.handler.handle()


def add_details():
    frappe.form_dict.cmd = "tenants_manager.api.subscription.add_owner_details"
    return frappe.handler.handle()


def delete_owner_data(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.delete_owner_data"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def force_delete_owner_data(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.delete_owner_data"
    frappe.form_dict.source_id = id
    frappe.form_dict.force = True
    return frappe.handler.handle()


def verify_email_via_code(id: str):
    frappe.form_dict.cmd = (
        "tenants_manager.api.subscription.verify_email_address_via_code"
    )
    frappe.form_dict.source_id = id
    return frappe.handler.handle()
  

def verify_email_via_link(id: str):
    frappe.form_dict.cmd = (
        "tenants_manager.api.subscription.verify_email_address_via_link"
    )
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def add_phone_number(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.add_phone_number"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def verify_phone_number_via_code(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.verify_phone_number"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def add_business_details(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.add_business_details"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def add_business_address(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.add_business_address"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def upload_owner_image(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.upload_owner_image"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def resend_email_otp(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.resend_email_otp"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def resend_sms_otp(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.subscription.resend_sms_otp"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


routes = [
    Rule("/business/wizard/setup-status", methods=["GET"], endpoint=get_status),
    Rule(
        "/business/wizard/is-email-registered",
        methods=["GET"],
        endpoint=is_email_registered,
    ),
    Rule("/business/wizard/owner-details", methods=["POST"], endpoint=add_details),
  
    Rule(
        "/business/<path:id>/wizard/delete",
        methods=["DELETE"],
        endpoint=delete_owner_data,
    ),
    Rule(
        "/business/<path:id>/wizard/force-delete",
        methods=["DELETE"],
        endpoint=force_delete_owner_data,
    ),
    Rule(
        "/business/<path:id>/wizard/verify-email-link",
        methods=["GET"],
        endpoint=verify_email_via_link,
    ),
    Rule(
        "/business/<path:id>/wizard/verify-email",
        methods=["PUT"],
        endpoint=verify_email_via_code,
    ),
    Rule(
        "/business/<path:id>/wizard/add-phone-number",
        methods=["PUT"],
        endpoint=add_phone_number,
    ),
    Rule(
        "/business/<path:id>/wizard/verify-phone-number",
        methods=["PUT"],
        endpoint=verify_phone_number_via_code,
    ),
    Rule(
        "/business/<path:id>/wizard/business-details",
        methods=["PUT"],
        endpoint=add_business_details,
    ),
    Rule(
        "/business/<path:id>/wizard/business-address",
        methods=["PUT"],
        endpoint=add_business_address,
    ),
    Rule(
        "/business/<path:id>/wizard/upload-owner-image",
        methods=["PUT"],
        endpoint=upload_owner_image,
    ),
    Rule(
        "/business/<path:id>/wizard/resend-email-otp",
        methods=["PUT"],
        endpoint=resend_email_otp,
    ),
    Rule(
        "/business/<path:id>/wizard/resend-sms-otp",
        methods=["PUT"],
        endpoint=resend_sms_otp,
    ),
]
