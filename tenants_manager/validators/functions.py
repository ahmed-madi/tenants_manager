import re
import frappe


def is_name_valid(name):
    pattern = r"^[A-Za-zÀ-ÿ' -]+$"
    return bool(re.match(pattern, name))


def is_email_valid(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_password(password):
    # Password must include at least one uppercase letter
    # Password must include at least one lowercase letter
    # Password must include at least one number
    # Password must include at least one special character
    # Password must not contain spaces

    pattern = (
        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_])\S{8,}$"
    )
    return bool(re.match(pattern, password))


def is_valid_phone_number(phone_number):
    from phonenumbers import NumberParseException, is_valid_number, parse
    from frappe import _

    if not phone_number:
        return False
    valid_number = False
    try:
        if valid_number := is_valid_number(parse(phone_number)):
            return True
    except NumberParseException as e:
        if e.error_type == NumberParseException.INVALID_COUNTRY_CODE:
            return False
    finally:
        if not valid_number:
            return False
        return True

def validate_string_for_domain(domain):
    if not isinstance(domain, str) or len(domain) == 0:
        return False

    # domain = domain.split(".")[0]
    pattern = r'^[a-zA-Z][a-zA-Z0-9-]*$'
    return bool(re.match(pattern, domain))