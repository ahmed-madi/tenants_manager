import frappe
from frappe.utils import flt, random_string, now, add_to_date
from tenants_manager.utils  import generate_random_numbers
def send_email_verification(email_address, name, check_if_sent=False):
    if check_if_sent:
        data = frappe.get_all(
            "Business Email Verification",
            filters={
                "business_owner_id": name,
                "business_owner_email": email_address,
                "status": "Active",
            },
            fields=["otp_sent_time", "otp_expiry_time", "otp_code"],
        )
        has_active = len(data) > 0
        if has_active:
            return data[0]

    doc = frappe.new_doc("Business Email Verification")
    expire_after = flt(
        frappe.db.get_single_value("Business Site Settings", "email_expire_time")
        or "90",
        2,
    )
    doc.business_owner_id = name
    doc.business_owner_email = email_address
    doc.otp_link_hash = random_string(32)
    doc.otp_code = generate_random_numbers()
    now_datetime = now()
    doc.otp_sent_time = now_datetime
    doc.otp_expiry_time = add_to_date(now_datetime, minutes=expire_after)

    doc.flags.ignore_permissions = True
    doc.save()
    return {
        "otp_sent_time": doc.otp_sent_time,
        "otp_expiry_time": doc.otp_expiry_time,
        # "otp_code": doc.otp_code,
    }


def send_sms_verification(phone_number, name, check_if_sent=False):
    if check_if_sent:
        data = frappe.get_all(
            "Business Phone Verification",
            filters={
                "business_owner_id": name,
                "business_owner_phone": phone_number,
                "status": "Active",
            },
            fields=["otp_sent_time", "otp_expiry_time", "otp_code"],
        )
        has_active = len(data) > 0
        if has_active:
            data[0]

    doc = frappe.new_doc("Business Phone Verification")
    expire_after = flt(
        frappe.db.get_single_value("Business Site Settings", "phone_expire_time")
        or "90",
        2,
    )
    doc.business_owner_id = name
    doc.business_owner_phone = phone_number
    doc.otp_link_hash = random_string(32)
    doc.otp_code = generate_random_numbers()
    now_datetime = now()
    doc.otp_sent_time = now_datetime
    doc.otp_expiry_time = add_to_date(now_datetime, minutes=expire_after)

    doc.flags.ignore_permissions = True
    doc.save()
    return {
        "otp_sent_time": doc.otp_sent_time,
        "otp_expiry_time": doc.otp_expiry_time,
        # "otp_code": doc.otp_code,
    }
