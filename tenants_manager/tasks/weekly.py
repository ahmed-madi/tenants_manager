import frappe


def clear_expired_email_otps():
    clear_expire("Business Email Verification")


def clear_expired_phone_otps():
    clear_expire("Business Phone Verification")


def clear_expire(dt):
    dt = frappe.qb.DocType(dt)
    frappe.qb.from_(dt).delete().where(dt.status == "Expired").run()
