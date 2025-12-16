ERRORS = {
    "VALIDATION_FAILED": {
        "status": "error",
        "error_code": "VALIDATION_FAILED",
        "message": "Input validation failed.",
        "details": {
            # "field_errors": {
            #     "email": "Email format is invalid.",
            #     "password": "Password must be at least 8 characters long.",
            # }
        },
        "status_code": 422  # Unprocessable Entity
    },
    "INVALID_OTP_CODE": {
        "status": "error",
        "error_code": "INVALID_OTP_CODE",
        "message": "Invalid OTP code or OTP code expired.",
        "details": {
            # "field_errors": {
            #     "email": "Email format is invalid.",
            #     "password": "Password must be at least 8 characters long.",
            # }
        },
        "status_code": 422  # Unprocessable Entity
    },
    "UNAUTHORIZED": {
        "status": "error",
        "error_code": "UNAUTHORIZED",
        "message": "Authentication required.",
        # "details": {"hint": "Please provide a valid API token."},
        "status_code": 401  # Unauthorized
    },
    "NOT_FOUND": {
        "status": "error",
        "error_code": "NOT_FOUND",
        "message": "The requested resource could not be found.",
        # "details": {"resource_type": "user", "resource_id": "12345"},
        "status_code": 404  # Not Found
    },
    "CONFLICT": {
        "status": "error",
        "error_code": "CONFLICT",
        "message": "The requested resource could not be updated.",
        # "details": {"resource_type": "user", "resource_id": "12345"},
        "status_code": 409  # Conflict
    },
    "INTERNAL_SERVER_ERROR": {
        "status": "error",
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred on the server.",
        "details": "Please try again later or contact support.",
        "status_code": 500  # Internal Server Error
    },
    "BAD_REQUEST": {
        "status": "error",
        "error_code": "BAD_REQUEST",
        "message": "Bad request.",
        "details": {},
        "status_code": 400  # Bad Request
    }
}


def get_message(error_code, details, timestamp, message=None):
    error = ERRORS[error_code]
    error.update(
        {
            "details": details,
            "timestamp": timestamp,
        }
    )
    if message:
        error.update(
            {
                "message": message,
            }
        )
    return error


def get_owner_message(status):
    messages = {
        "Owner Info Completed": "Please Verify Your Email Via OTP Code",
        "Email Verified": "Please Add Your Phone Number",
        "Phone Number Added": "Please Verify Phone Number Via OTP Code",
        "Phone Number Verified": "Please Add Your Business Details",
        "Business Info Completed": "Please Add Your Business Address",
        "Business Address Completed": "Please Upload Your Image",
        "Completed": "All Steps Are Done",
    }
    return messages.get(status)

def get_business_message(status):
    messages = {
        "Business Name Added": "Please upload your store's logo",
        "Logo Added": "Please provide your store's atmosphere",
        "Atmosphere Keywords Added": "Please provide your store's specialties",
        "Specialties Keywords Added": "Please add what make you unique",
        "Uniqueness Keywords Added": "All Steps Are Done",
        "Completed": "All Steps Are Done",
    }
    return messages.get(status)


def get_status_message(status, doctype="Business Owner"):
    if doctype == "Business":
        return get_business_message(status)
    return get_owner_message(status)
