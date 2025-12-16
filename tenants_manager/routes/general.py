import frappe

from werkzeug.routing import Rule


def get_business_types():
    frappe.form_dict.cmd = "tenants_manager.api.subscription.business_types"
    return frappe.handler.handle()


def get_countries():
    frappe.form_dict.cmd = "tenants_manager.api.subscription.countries"
    return frappe.handler.handle()


routes = [
    Rule("/business/types", methods=["GET"], endpoint=get_business_types),
    Rule("/business/countries", methods=["GET"], endpoint=get_countries),
]
