import frappe
from frappe.utils import now


def expire_email_otps():
    set_expire("Business Email Verification")


def expire_phone_otps():
    set_expire("Business Phone Verification")


def set_expire(dt):
    dt = frappe.qb.DocType(dt)
    frappe.qb.update(dt).set(dt.status, "Expired").where(
        dt.otp_expiry_time <= now()
    ).where(dt.status == "Active").run()
