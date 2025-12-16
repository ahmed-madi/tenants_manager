import frappe
from frappe.utils import cint
from tenants_manager.utils.otp import send_email_verification, send_sms_verification

from tenants_manager.api.utils.files import decode_base64_to_binary, guess_mime_type
from frappe.utils import now_datetime
from frappe.utils.file_manager import save_file

from tenants_manager.api.utils.response import (
    build_response,
    build_error_response,
)
from tenants_manager.api.utils import (
    check_business_owner,
    check_business,
    get_business_next_status_step,
    is_doc_status_valid_to_update,
    is_doc_status_after_current,
)
from tenants_manager.validators.helper import (
    validate_business_legal,
    validate_business_keywords,
    validate_domain,
)
from tenants_manager.validators.messages import get_status_message


@frappe.whitelist(methods=["POST"], xss_safe=True)
def add_business_for_owner(source_id="", business_name=""):
    field_errors = validate_business_legal(business_name)
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {"field_errors": field_errors}, 422
        )
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    status = "Business Name Added"
    doc = frappe.new_doc("Business")
    doc.business_owner = name
    doc.business_name = business_name
    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "business_name": doc.business_name,
        "domain_name": doc.domain_name,
        "owner_id": doc.business_owner,
        "owner_full_name": doc.full_name,
        "owner_email_address": doc.email_address,
        "owner_phone_number": doc.phone_number,
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_business_next_status_step(status)).replace(
            "_", "-"
        ),
        "message": get_status_message(status, doctype="Business"),
        "source_type": "Business",
    }

    build_response(data, "Business Created for Business Owner", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def upload_business_logo(
    source_id="",
    business_id="",
    business_logo="",
):
    if not isinstance(business_logo, str) or len(business_logo) == 0:
        return build_error_response(
            "VALIDATION_FAILED",
            {
                "field_errors": {
                    "business_logo": "file is missing, upload image file",
                }
            },
            422,
        )
    content = decode_base64_to_binary(business_logo)
    type = guess_mime_type(content)
    if type not in ["png", "jpeg", "bmp"]:
        return build_error_response(
            "VALIDATION_FAILED",
            {
                "field_errors": {
                    "business_logo": "can not detect image, upload valid mage type (png, jpeg, bmp)",
                }
            },
            422,
        )
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    b_name = check_business(business_id)
    if not b_name or b_name is None:
        return

    doc = frappe.get_doc("Business", b_name)
    # check if business belong to owner!
    if doc.business_owner != name:
        build_error_response(
            "CONFLICT",
            {
                "resource_type": "Business",
                "resource_id": b_name,
                "owner_id": name,
            },
            409,
            "The resource could not be updated Due to conflict of the owner",
        )
        return

    status = "Logo Added"
    # check if current step is valid and prev. steps are completed!
    if not is_doc_status_valid_to_update(
        doc.status, status, doc.name, doctype="Business"
    ):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status, doctype="Business"):
        status = doc.status

    field_name = "business_logo"
    api_filename = "business_logo"

    file_name = str(now_datetime().timestamp()).replace(".", "") + "." + type
    # file = upload_file(field_name, api_filename, build_error_res=True)
    # if not file or file is None:
    #     return
    file = save_file(
        file_name, content, "Business", doc.name, is_private=1, df=field_name
    )
    doc.business_logo = file.file_url
    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()

    data = {
        "source_id": doc.name,
        "business_name": doc.business_name,
        "domain_name": doc.domain_name,
        "business_logo": doc.business_logo,
        "owner_id": doc.business_owner,
        "owner_full_name": doc.full_name,
        "owner_email_address": doc.email_address,
        "owner_phone_number": doc.phone_number,
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_business_next_status_step(status)).replace(
            "_", "-"
        ),
        "message": get_status_message(status, doctype="Business"),
        "source_type": "Business",
    }
    build_response(data, "Business logo Uploaded", 200)


@frappe.whitelist(methods=["GET"], xss_safe=True)
def get_business_details_for_owner(source_id=""):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    doc = frappe.get_doc("Business Owner", name)

    data = {
        "source_id": doc.name,
        "business_type": doc.business_type,
        "business_legal_name": doc.business_legal_name,
        "business_id": doc.business_id,
        "status": doc.status,
        "is_email_verified": bool(doc.is_email_verified),
        "is_phone_verified": bool(doc.is_phone_verified),
        "source_type": "Business Owner",
    }

    build_response(data, "Retrieve Business Details for Owner Successfully", 200)


@frappe.whitelist(methods=["GET"], xss_safe=True)
def get_all_business_for_owner(source_id=""):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    doc = frappe.get_doc("Business Owner", name)
    business_list = frappe.db.sql(
        "SELECT name, business_name, business_logo FROM `tabBusiness` WHERE business_owner='{}'".format(
            doc.name
        ),
        as_dict=True,
    )
    data = {
        "source_id": doc.name,
        "business_type": doc.business_type,
        "business_legal_name": doc.business_legal_name,
        "business_id": doc.business_id,
        "status": doc.status,
        "is_email_verified": bool(doc.is_email_verified),
        "is_phone_verified": bool(doc.is_phone_verified),
        "business_list": business_list,
        "source_type": "Business Owner",
    }

    build_response(data, "Retrieve All Business Details for Owner Successfully", 200)


@frappe.whitelist(methods=["GET"], xss_safe=True)
def get_keywords(keyword_type=""):
    keywords = frappe.db.sql(
        "SELECT name, keyword FROM `tabDescription Keyword` WHERE keyword_type='{}'".format(
            keyword_type
        ),
        as_dict=True,
    )
    data = {
        "keyword_list": keywords,
        "source_type": "Description Keyword",
    }

    build_response(data, "Retrieve Description Keywords Successfully", 200)


@frappe.whitelist(methods=["PUT"], xss_safe=True)
def add_business_keywords(source_id="", business_id="", keyword_type="", keywords=[]):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    b_name = check_business(business_id)
    if not b_name or b_name is None:
        return

    doc = frappe.get_doc("Business", b_name)
    # check if business belong to owner!
    if doc.business_owner != name:
        build_error_response(
            "CONFLICT",
            {
                "resource_type": "Business",
                "resource_id": b_name,
                "owner_id": name,
            },
            409,
            "The resource could not be updated Due to conflict of the owner",
        )
        return

    field_errors = validate_business_keywords(keywords, keyword_type)
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {"field_errors": field_errors}, 422
        )

    if keyword_type == "Atmosphere":
        status = "Atmosphere Keywords Added"
        doc.atmosphere_keywords = []
        doc.atmosphere_keywords_added = 1
        for k in keywords:
            doc.append("atmosphere_keywords", {"keyword": k})
    elif keyword_type == "Specialties":
        status = "Specialties Keywords Added"
        doc.specialties_keywords = []
        doc.specialties_keywords_added = 1
        for k in keywords:
            doc.append("specialties_keywords", {"keyword": k})
    elif keyword_type == "Uniqueness":
        status = "Completed"
        doc.uniqueness_keywords = []
        doc.uniqueness_keywords_added = 1
        for k in keywords:
            doc.append("uniqueness_keywords", {"keyword": k})

    if not is_doc_status_valid_to_update(
        doc.status, status, doc.name, doctype="Business"
    ):
        return

    # update status?
    if is_doc_status_after_current(doc.status, status, doctype="Business"):
        status = doc.status

    doc.status = status
    doc.flags.ignore_permissions = True
    doc.save()
    data = {
        "source_id": doc.name,
        "business_name": doc.business_name,
        "domain_name": doc.domain_name,
        "business_logo": doc.business_logo,
        "owner_id": doc.business_owner,
        "owner_full_name": doc.full_name,
        "owner_email_address": doc.email_address,
        "owner_phone_number": doc.phone_number,
        "atmosphere_keywords": [k.keyword for k in doc.atmosphere_keywords],
        "specialties_keywords": [k.keyword for k in doc.specialties_keywords],
        "uniqueness_keywords": [k.keyword for k in doc.uniqueness_keywords],
        "current_status": frappe.scrub(status).replace("_", "-"),
        "next_step": frappe.scrub(get_business_next_status_step(status)).replace(
            "_", "-"
        ),
        "message": get_status_message(status, doctype="Business"),
        "source_type": "Business",
    }
    build_response(data, f"Business {keyword_type} Keywords Updated", 200)


@frappe.whitelist(methods=["GET"], xss_safe=True)
def get_business_keywords(
    source_id="",
    business_id="",
    keyword_type="",
):
    name = check_business_owner(source_id)
    if not name or name is None:
        return

    b_name = check_business(business_id)
    if not b_name or b_name is None:
        return

    doc = frappe.get_doc("Business", b_name)
    # check if business belong to owner!
    if doc.business_owner != name:
        build_error_response(
            "CONFLICT",
            {
                "resource_type": "Business",
                "resource_id": b_name,
                "owner_id": name,
            },
            409,
            "The resource could not be updated Due to conflict of the owner",
        )
        return

    keywords = []
    if keyword_type == "Atmosphere":
        keywords = [k.keyword for k in doc.atmosphere_keywords]
    elif keyword_type == "Specialties":
        keywords = [k.keyword for k in doc.specialties_keywords]
    elif keyword_type == "Uniqueness":
        keywords = [k.keyword for k in doc.uniqueness_keywords]
    data = {
        "source_id": doc.name,
        "business_name": doc.business_name,
        "owner_id": doc.business_owner,
        "keywords": keywords,
        "source_type": "Business",
    }
    build_response(data, f"Retrieve Business {keyword_type} Keywords", 200)


@frappe.whitelist(methods=["GET"], xss_safe=True)
def is_domain_available(business_name=""):
    field_errors = validate_business_legal(business_name)
    if field_errors:
        return build_error_response(
            "VALIDATION_FAILED", {
                "field_errors": field_errors,
                "is_domain_available": False,
                "check_for_domain": business_name,
            }, 422
        )
    # field_errors = validate_domain(business_name)
    # if field_errors:
    #    return build_error_response(
    #        "VALIDATION_FAILED",
    #        {"field_errors": field_errors},
    #         422,
    #    )
    # origin_domain = domain
    # domain = domain.split(".")[0]
    # business_name = business_name.lower()
    # is_taken = frappe.db.get_value(
    #   "Business Site", {"site_name": ["LIKE", f"{business_name}.%"]}, "name"
    # )

    data = {
        "is_domain_available": True,
        "check_for_domain": business_name,
        "your_domain": business_name.replace(" ", "-").lower(),
    }
    build_response(data, "Check Domain name")
