import frappe
from frappe.utils import is_invalid_date_string

from tenants_manager.validators.functions import (
    is_email_valid,
    is_name_valid,
    is_valid_password,
    is_valid_phone_number,
    validate_string_for_domain,
)


def validate_name(name, other):
    if not name:
        return f"{other} cannot be empty. Please enter value."
    if not isinstance(name, str):
        return f"{other} can only contain alphabetic characters (A-Z, a-z) and spaces. Special characters are not allowed."

    name = name.strip()
    if len(name) < 1 or len(name) > 50:
        return f"{other} must be between 1 and 50 characters long. Please adjust your input."
    if not is_name_valid(name):
        return f"{other} can only contain alphabetic characters (A-Z, a-z) and spaces. Special characters are not allowed."

    return None


def is_valid_str(string, other):
    if not string:
        return f"{other} cannot be empty. Please enter value."
    if not isinstance(string, str):
        return f"{other} can only contain alphabetic characters (A-Z, a-z) and spaces. Special characters are not allowed."

    string = string.strip()
    if len(string) < 1 or len(string) > 50:
        return f"{other} must be between 1 and 50 characters long. Please adjust your input."


def validate_email(email):
    if not email:
        return "Email address cannot be empty. Please enter your email address."
    if "@" not in email:
        return "Email address must contain an '@' symbol. Please check your input."
    if len(email) > 254:
        return "Email address must be less than 254 characters long. Please shorten your input."
    if not is_email_valid(email):
        return "The email address provided is invalid. Please ensure it follows the format: example@domain.com."

    return None


def validate_date(date):
    if not date:
        return "Date cannot be empty. Please enter your date."
    if not isinstance(date, str):
        return "The Date provided is invalid"

    date_format = (
        frappe.db.get_single_value("System Settings", "date_format") or "dd-mm-yyyy"
    )
    if is_invalid_date_string(date):
        return f"The Date provided is invalid. Please ensure it follows the format: {date_format}."

    return None


def validate_password(password):
    if not password or not isinstance(password, str) or not is_valid_password(password):
        return "Password validation failed."

    return None


def validate_owner_details(
    first_name, last_name, email_address, password, confirm_password, date_of_birth
):
    field_errors = {}
    validate = validate_name(first_name, "First Name")
    if validate is not None:
        field_errors.update(
            {
                "first_name": validate,
            }
        )
    validate = validate_name(last_name, "Last Name")
    if validate is not None:
        field_errors.update(
            {
                "last_name": validate,
            }
        )
    validate = validate_email(email_address)
    if validate is not None:
        field_errors.update(
            {
                "email_address": validate,
            }
        )
    validate = validate_date(date_of_birth)
    if validate is not None:
        field_errors.update(
            {
                "date_of_birth": validate,
            }
        )
    validate = validate_owner_passwords(password, confirm_password)
    if validate is not None:
        field_errors.update(validate)
    return field_errors


def validate_owner_passwords(password, confirm_password):
    field_errors = {}
    validate = validate_password(password)
    if validate is not None:
        field_errors.update(
            {
                "password": validate,
                "password_polices": [
                    "Minimum length of 8 characters",
                    "At least 1 uppercase letter",
                    "At least 1 lowercase letter.",
                    "At least 1 digit",
                    "At least 1 special character",
                    "Must not contain spaces",
                ],
            }
        )
        return field_errors

    if password != confirm_password:
        field_errors.update(
            {
                "confirm_password": "Passwords does not matched.",
                "password_polices": [
                    "Password must be at least 8 characters long.",
                    "Password must contain at least 1 uppercase letter.",
                    "Password must contain at least 1 lowercase letter.",
                    "Password must contain at least 1 digit.",
                    "Password must contain at least 1 special character.",
                    "Password must not contain spaces",
                ],
            }
        )
        return field_errors


def validate_owner_phone_number(phone_number):
    field_errors = {}
    if not is_valid_phone_number(phone_number):
        field_errors.update(
            {
                "phone_number": f"Phone Number {phone_number} is not valid, Please add valid phone number with country code",
            }
        )
    return field_errors


def validate_business_details(business_type, business_legal_name, business_id):
    field_errors = {}
    validate = is_valid_str(business_type, "Business Type")
    if validate is not None:
        field_errors.update(
            {
                "business_type": validate,
            }
        )
    validate = is_valid_str(business_legal_name, "Business Legal Name")
    if validate is not None:
        field_errors.update(
            {
                "business_legal_name": validate,
            }
        )
    validate = is_valid_str(business_id, "Business ID")
    if validate is not None:
        field_errors.update(
            {
                "business_id": validate,
            }
        )

    return field_errors


def validate_business_address(address_line_1, city, state, zip_code, country):
    field_errors = {}
    validate = is_valid_str(address_line_1, "Business Address")
    if validate is not None:
        field_errors.update(
            {
                "address_line_1": validate,
            }
        )
    validate = is_valid_str(city, "City")
    if validate is not None:
        field_errors.update(
            {
                "city": validate,
            }
        )
    validate = is_valid_str(state, "State")
    if validate is not None:
        field_errors.update(
            {
                "state": validate,
            }
        )

    validate = is_valid_str(zip_code, "ZIP Code")
    if validate is not None:
        field_errors.update(
            {
                "zip_code": validate,
            }
        )

    validate = is_valid_str(country, "Country")
    if validate is not None:
        field_errors.update(
            {
                "country": validate,
            }
        )

    return field_errors


def validate_business_legal(business_legal_name):
    field_errors = {}

    validate = is_valid_str(business_legal_name, "Business Legal Name")
    if validate is not None:
        field_errors.update(
            {
                "business_name": validate,
            }
        )
    if (
        len(frappe.get_all("Business", filters={"business_name": business_legal_name}))
        > 0
    ):
        field_errors.update(
            {
                "business_name": "Business name is already in use, select another name please",
            }
        )
    return field_errors


def validate_business_keywords(keywords, type=""):
    field_errors = {}

    if not isinstance(keywords, list) or len(keywords) == 0:
        field_errors.update(
            {
                "keywords": "Please Add keywords in list format, ['k1', 'k2',]",
            }
        )
        return field_errors

    for k in keywords:
        if not isinstance(k, str):
            field_errors.update(
                {
                    "keywords": "Please Add keywords in list format, ['k1', 'k2',]",
                }
            )
            return field_errors

        exists = frappe.db.exists("Description Keyword", k)
        if not exists:
            d = frappe.new_doc("Description Keyword")
            d.update({"keyword": k, "keyword_type": type})
            d.flags.ignore_permissions = True
            d.save()

    return field_errors


def validate_domain(domain):
    field_errors = {}
    validate = validate_string_for_domain(domain)
    if not validate:
        field_errors.update(
            {
                "domain": "Domain name must contain (letters, number, -) and must start with a letter",
            }
        )
    return field_errors
