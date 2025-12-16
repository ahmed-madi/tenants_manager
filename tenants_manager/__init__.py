__version__ = "0.0.1"

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from enum import Enum

from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Submount
from werkzeug.wrappers import Request, Response

import frappe
import frappe.client
from frappe import _
from frappe.utils.response import build_response
import frappe.handler

from tenants_manager.routes.wizard import routes as wizard_routes
from tenants_manager.routes.general import routes as general_routes
from tenants_manager.routes.business import routes as business_routes


class ApiVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"


def handle(request: Request):
    try:
        endpoint, arguments = API_URL_MAP.bind_to_environ(request.environ).match()
    except NotFound:  # Wrap 404 - backward compatiblity
        raise frappe.DoesNotExistError

    data = endpoint(**arguments)
    if isinstance(data, Response):
        return data

    if data is not None:
        frappe.response["data"] = data
    return build_response("json")


# Merge all API version routing rules
from frappe.api.v1 import url_rules as v1_rules
from frappe.api.v2 import url_rules as v2_rules

custom_end_points = wizard_routes + general_routes + business_routes

for ep in custom_end_points:
    v1_rules.append(ep)

API_URL_MAP = Map(
    [
        # V1 routes
        Submount("/api", v1_rules),
        Submount(f"/api/{ApiVersion.V1.value}", v1_rules),
        Submount(f"/api/{ApiVersion.V2.value}", v2_rules),
    ],
    strict_slashes=False,  # Allows skipping trailing slashes
    merge_slashes=False,
)

frappe.api.handle = handle
