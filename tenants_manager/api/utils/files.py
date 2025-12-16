from mimetypes import guess_type
from tenants_manager.api.utils.response import (
    build_response,
    build_error_response,
)

import frappe


def upload_file(field_name, api_filename, build_error_res=False):
    files = frappe.request.files
    if api_filename not in files:
        if build_error_res:
            build_error_response(
                "VALIDATION_FAILED",
                {
                    "field_errors": {
                        f"{field_name}": "file is missing, upload image file",
                    }
                },
                422,
            )
        return None
    file = frappe.request.files[api_filename]
    content = file.stream.read()
    filename = file.filename
    content_type = guess_type(filename)[0]

    if content is None or filename is None or content_type is None:
        if build_error_res:
            build_error_response(
                "VALIDATION_FAILED",
                {
                    "field_errors": {
                        f"{field_name}": "file is missing, upload image file",
                    }
                },
                422,
            )
        return None

    if not content_type.startswith("image/"):
        if build_error_res:
            build_error_response(
                "VALIDATION_FAILED",
                {
                    "field_errors": {
                        f"{field_name}": "upload image file only",
                    }
                },
                422,
            )
        return None
    file_doc = frappe.get_doc(
        {
            "doctype": "File",
            "folder": "Home",
            "file_name": filename,
            "is_private": 1,
            "content": content,
        }
    ).save(ignore_permissions=True)

    return file_doc

import base64
import re
import mimetypes

def decode_base64_to_binary(content):
    if isinstance(content, str):
        content = content.encode("utf-8")

    if b"," in content:
        content = content.split(b",")[1]
    content = base64.b64decode(content + b"===")

    return content

def guess_mime_type(binary_data):
    if binary_data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif binary_data.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    # elif binary_data[:3] in [b'GIF87', b'GIF89']:
    #     return 'gif'
    elif binary_data[:2] == b'BM':
        return 'bmp'
    else:
        return None