import frappe
from frappe.utils import cint, now_datetime
from tenants_manager.utils.otp import send_email_verification, send_sms_verification

from tenants_manager.api.utils.files import decode_base64_to_binary, guess_mime_type
from frappe.utils.file_manager import save_file

from tenants_manager.api.utils.response import (
    build_response,
    build_error_response,
)
from tenants_manager.api.utils import (
    get_owner_next_status_step,
    is_doc_status_valid_to_update,
    is_doc_status_after_current,
    check_business_owner,
)
from tenants_manager.validators.helper import (
    validate_owner_details,
    validate_owner_passwords,
    validate_owner_phone_number,
    validate_business_details,
    validate_business_address,
    validate_email,
)
from tenants_manager.validators.messages import get_status_message


@frappe.whitelist(methods=["GET"], xss_safe=True)
def check_email_address(email=""):
    validate = validate_email(email)
    if validate is not None:
        return build_error_response(
            "VALIDATION_FAILED",
            {
                "field_errors": {
                    "email": validate,
                }
            },
            422,
        )

    status = (
        frappe.db.get_value("Business Owner", {"email_address": email}, "status")
        or "New"
    )
    name = (
        frappe.db.get_value("Business Owner", {"email_address": email}, "name") or "New"
    )
    data = {
        "source_id": name,
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
    }
    build_response(data, "Check Next Status Details")


@frappe.whitelist(methods=["GET"], xss_safe=True)
def is_email_registered(email=""):
    validate = validate_email(email)
    if validate is not None:
        return build_error_response(
            "VALIDATION_FAILED",
            {
                "field_errors": {
                    "email": validate,
                }
            },
            422,
        )

    name = frappe.db.get_value("Business Owner", {"email_address": email}, "name")
    response = {"is_email_registered": bool(name)}
    build_response(response, "Check In Use Email")


@frappe.whitelist(methods=["POST"], xss_safe=True)
def add_owner_details(
    first_name="",
    last_name="",
    email_address="",
    password="",
    confirm_password="",
    date_of_birth="",
):
    field_errors = validate_owner_details(
        first_name, last_name, email_address, password, confirm_password, date_of_birth
    )
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {"field_errors": field_errors}, 422
        )

    doc = None
    status_code = 201
    msg = "Business Owner Created"
    status = "Owner Info Completed"

    name = (
        frappe.get_value("Business Owner", {"email_address": email_address}, "name")
        or None
    )

    is_new = False
    if name:
        doc = frappe.get_doc("Business Owner", name)
        status_code = 200
        msg = "Business Owner Updated"
        status = doc.status
    else:
        doc = frappe.new_doc("Business Owner")
        doc.update({"email_address": email_address, "status": status})
        is_new = True

    doc.update(
        {
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "date_of_birth": date_of_birth,
        }
    )

    message = get_status_message
    if is_new:
        doc.is_email_verified = 0
        message = "Please Verify Your Email Via OTP Code"
    else:
        message = get_status_message(doc.status)

    doc.flags.ignore_permissions = True
    doc.save()

    # expire all codes
    frappe.db.sql(
        "UPDATE `tabBusiness Email Verification` SET status='Expired' WHERE business_owner_id='{}'".format(
            doc.name
        )
    )

    data = {
        "source_id": doc.name,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": message,
        "source_type": "Business Owner",
    }

    if doc.is_email_verified == 0:
        data.update(send_email_verification(doc.email_address, doc.name))

    build_response(data, msg, status_code)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def verify_email_address_via_code(source_id="", otp_code=""):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    doc = frappe.get_doc("Business Owner", name)
    status = "Email Verified"
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    # check if active otp code
    can_active = (
        len(
            frappe.get_all(
                "Business Email Verification",
                filters={
                    "business_owner_id": name,
                    "business_owner_email": doc.email_address,
                    "status": "Active",
                    "otp_code": otp_code,
                },
            )
        )
        > 0
    )

    if not can_active:
        return build_error_response(
            "INVALID_OTP_CODE",
            {"field_errors": {"otp_code": otp_code}},
            422,
        )
    # expire all codes
    frappe.db.sql(
        "UPDATE `tabBusiness Email Verification` SET status='Expired' WHERE business_owner_id='{}'".format(
            doc.name
        )
    )
    doc.status = status
    doc.is_email_verified = 1
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    build_response(data, "Email Verified for Business Owner", 200)


# @frappe.whitelist(allow_guest=True, methods=["GET"], xss_safe=True)
# def verify_email_address_via_link(source_id="", hash_code="", otp_code=""):
#     name = check_business_owner(source_id)
#     if not name or name is None:
#         return

#     doc = frappe.get_doc("Business Owner", name)
#     status = "Email Verified"
#     # check if current step is valid and prev. steps are completed!
#     if not is_doc_status_valid_to_update(doc.status, status, doc.name):
#         return

#     # update status?
#     if is_doc_status_after_current(doc.status, status):
#         status = doc.status

#     # check if active otp code
#     can_active = (
#         len(
#             frappe.get_all(
#                 "Business Email Verification",
#                 filters={
#                     "business_owner_id": name,
#                     "business_owner_email": doc.email_address,
#                     "status": "Active",
#                     "otp_link_hash": hash_code,
#                     "otp_code": otp_code,
#                 },
#             )
#         )
#         > 0
#     )

#     if not can_active:
#         return build_error_response(
#             "INVALID_OTP_CODE",
#             {"field_errors": {"otp_code": hash_code}},
#             422,
#         )
#     # expire all codes
#     frappe.db.sql(
#         "UPDATE `tabBusiness Email Verification` SET status='Expired' WHERE business_owner_id='{}'".format(
#             doc.name
#         )
#     )
#     doc.status = status
#     doc.is_email_verified = 1
#     doc.flags.ignore_permissions = True
#     doc.save()
#     data = {
#         "source_id": doc.name,
#         "first_name": doc.first_name,
#         "last_name": doc.last_name,
#         "email_address": doc.email_address,
#         "is_email_verified": bool(doc.is_email_verified),
#         "current_status": frappe.scrub(status).replace("_", "-"),
#         "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
#         "message": get_status_message(doc.status),
#         "source_type": "Business Owner",
#     }
#     build_response(data, "Email Verified for Business Owner", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def add_phone_number(source_id="", phone_number=""):
    field_errors = validate_owner_phone_number(phone_number)
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {"field_errors": field_errors}, 422
        )

    name = check_business_owner(source_id)
    if not name or name is None:
        return
    status = "Phone Number Added"
    doc = frappe.get_doc("Business Owner", name)
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    is_new_phone = doc.phone_number != phone_number
    message = get_status_message(doc.status)
    if is_new_phone:
        doc.is_phone_verified = 0
        message = "Please Verify Phone Number Via OTP Code"
    doc.phone_number = phone_number
    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "is_phone_verified": bool(doc.is_phone_verified),
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": message,
        "source_type": "Business Owner",
    }
    # expire all codes
    frappe.db.sql(
        "UPDATE `tabBusiness Phone Verification` SET status='Expired' WHERE business_owner_id='{}'".format(
            doc.name
        )
    )
    # if new phone or no active activation code
    active_otps = frappe.get_all(
        "Business Phone Verification",
        filters={
            "business_owner_id": name,
            "business_owner_phone": phone_number,
            "status": "Active",
        },
    )
    if doc.is_phone_verified == 0:
        data.update(send_sms_verification(doc.phone_number, doc.name))

    if len(active_otps) > 0:
        active_otp = active_otps[0]
        data.update(
            {
                "otp_sent_time": active_otp.otp_sent_time,
                "otp_expiry_time": active_otp.otp_expiry_time,
                "otp_code": active_otp.otp_code,
            }
        )

    build_response(
        data, "Phone Number added for Business Owner, check SMS for verification", 200
    )


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def verify_phone_number(source_id="", phone_number="", otp_code=""):
    name = (
        frappe.get_value(
            "Business Owner",
            {
                "name": source_id or "",
                "phone_number": phone_number or "",
            },
            "name",
        )
        or None
    )
    if not name:
        return build_error_response(
            "NOT_FOUND",
            {"resource_type": "Business Owner", "resource_id": source_id or ""},
            404,
            "The requested resource could not be found or dose not match with email or phone number",
        )

    status = "Phone Number Verified"
    doc = frappe.get_doc("Business Owner", name)
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    # check if active otp code
    can_active = (
        len(
            frappe.get_all(
                "Business Phone Verification",
                filters={
                    "business_owner_id": name,
                    "business_owner_phone": phone_number,
                    "status": "Active",
                    "otp_code": otp_code,
                },
            )
        )
        > 0
    )

    if not can_active:
        return build_error_response(
            "INVALID_OTP_CODE",
            {"field_errors": {"otp_code": otp_code}},
            422,
        )
    # expire all codes
    frappe.db.sql(
        "UPDATE `tabBusiness Phone Verification` SET status='Expired' WHERE business_owner_id='{}' AND business_owner_phone='{}'".format(
            name, phone_number
        )
    )
    doc.status = status
    doc.is_phone_verified = 1
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    build_response(data, "Phone Number Verified for Business Owner", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def add_business_details(
    source_id="",
    business_type="",
    business_legal_name="",
    business_id="",
):
    field_errors = validate_business_details(
        business_type, business_legal_name, business_id
    )
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {"field_errors": field_errors}, 422
        )

    if not frappe.db.exists("Business Type", business_type):
        return build_error_response(
            "NOT_FOUND",
            {"resource_type": "Business Type", "resource_id": business_type},
            404,
            "The requested resource could not be found or dose exists, please select a valid Business Type",
        )

    name = check_business_owner(source_id)
    if not name or name is None:
        return
    status = "Business Info Completed"
    doc = frappe.get_doc("Business Owner", name)
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    doc.business_type = business_type
    doc.business_legal_name = business_legal_name
    doc.business_id = business_id
    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()

    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "is_phone_verified": bool(doc.is_phone_verified),
        "business_type": doc.business_type,
        "business_legal_name": doc.business_legal_name,
        "business_id": doc.business_id,
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    build_response(data, "Business Info added to Business Owner", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def add_business_address(
    source_id="",
    address_line_1="",
    address_line_2="",
    city="",
    state="",
    zip_code="",
    country="",
):
    # address_line_2 optional
    field_errors = validate_business_address(
        address_line_1, city, state, zip_code, country
    )
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {"field_errors": field_errors}, 422
        )

    if not frappe.db.exists("Country", country):
        return build_error_response(
            "NOT_FOUND",
            {"resource_type": "Country", "resource_id": country},
            404,
            "The requested resource could not be found or dose exists, please select a valid Country",
        )

    name = check_business_owner(source_id)
    if not name or name is None:
        return
    status = "Business Address Completed"
    doc = frappe.get_doc("Business Owner", name)
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    doc.address_line_1 = address_line_1
    doc.address_line_2 = address_line_2 or ""
    doc.city = city
    doc.state = state
    doc.zip_code = zip_code
    doc.zip_code = zip_code
    doc.country = country
    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()

    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "is_phone_verified": bool(doc.is_phone_verified),
        "business_type": doc.business_type,
        "business_legal_name": doc.business_legal_name,
        "business_id": doc.business_id,
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    build_response(data, "Business Info added to Business Owner", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def upload_owner_image(
    source_id="",
    profile_image=""
):
    if not isinstance(profile_image, str) or len(profile_image) == 0:
        return build_error_response(
            "VALIDATION_FAILED",
            {
                "field_errors": {
                    "profile_image": "file is missing, upload image file",
                }
            },
            422,
        )
    content = decode_base64_to_binary(profile_image)
    type = guess_mime_type(content)
    if type not in ["png", "jpeg", "bmp"]:
        return build_error_response(
            "VALIDATION_FAILED",
            {
                "field_errors": {
                    "profile_image": "can not detect image, upload valid mage type (png, jpeg, bmp)",
                }
            },
            422,
        )
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    status = "Completed"
    doc = frappe.get_doc("Business Owner", name)
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status
    file_name = str(now_datetime().timestamp()).replace('.', '') + '.' + type
    file = save_file(file_name, content, "Business Owner", doc.name, is_private=1, df="owner_profile_image")
    if not file or file is None:
        return
    doc.owner_profile_image = file.file_url
    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()

    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "profile_image": doc.owner_profile_image,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "is_phone_verified": bool(doc.is_phone_verified),
        "business_type": doc.business_type,
        "business_legal_name": doc.business_legal_name,
        "business_id": doc.business_id,
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    build_response(data, "Business Owner Profile Uploaded", 200)


@frappe.whitelist(methods=["GET"])
def business_types():
    data = frappe.db.sql(
        "SELECT name, business_type as label FROM `tabBusiness Type`", as_dict=True
    )
    build_response(data, "Retrieve Business Types Successfully", 200)


@frappe.whitelist(methods=["GET"])
def countries():
    data = frappe.db.sql(
        "SELECT name, code, country_name as label FROM `tabCountry`", as_dict=True
    )
    build_response(data, "Retrieve Countries Successfully", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def resend_email_otp(source_id=""):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    doc = frappe.get_doc("Business Owner", name)
    status = "Owner Info Completed"
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    # expire all codes
    frappe.db.sql(
        "UPDATE `tabBusiness Email Verification` SET status='Expired' WHERE business_owner_id='{}'".format(
            doc.name
        )
    )

    doc.status = status
    if (
        cint(
            frappe.db.get_single_value(
                "Business Site Settings", "expire_email_on_resend_otp"
            )
        )
        == 1
    ):
        doc.is_email_verified = 0
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "is_phone_verified": bool(doc.is_phone_verified),
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    data.update(send_email_verification(doc.email_address, doc.name))
    build_response(data, "Email OTP Resend Successfully", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def resend_sms_otp(source_id=""):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    doc = frappe.get_doc("Business Owner", name)
    status = "Phone Number Verified"
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(doc.status, status, doc.name):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status):
        status = doc.status

    # expire all codes
    frappe.db.sql(
        "UPDATE `tabBusiness Phone Verification` SET status='Expired' WHERE business_owner_id='{}'".format(
            doc.name
        )
    )

    doc.status = status
    if (
        cint(
            frappe.db.get_single_value(
                "Business Site Settings", "expire_phone_on_resend_otp"
            )
        )
        == 1
    ):
        doc.is_phone_verified = 0
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "is_phone_verified": bool(doc.is_phone_verified),
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_owner_next_status_step(status)).replace("_", "-"),
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }
    data.update(send_sms_verification(doc.phone_number, doc.name))
    build_response(data, "Phone number OTP Resend Successfully", 200)


@frappe.whitelist(methods=["DELETE"], xss_safe=True)
def delete_owner_data(
    source_id="",
    force=False,
):
    name = check_business_owner(source_id)
    if not name or name is None:
        return
    doc = frappe.get_doc("Business Owner", name)
    doc.delete(force=force, ignore_permissions=True)

    data = {
        "source_id": doc.name,
        "first_name": doc.first_name,
        "last_name": doc.last_name,
        "email_address": doc.email_address,
        "is_email_verified": bool(doc.is_email_verified),
        "phone_number": doc.phone_number,
        "next_step": "Business Owner Deleted",
        "message": get_status_message(doc.status),
        "source_type": "Business Owner",
    }

    build_response(data, "Business Owner Deleted Successfully", 200)
