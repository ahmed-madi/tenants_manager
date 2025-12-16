import frappe

from werkzeug.routing import Rule


def get_atmosphere_keywords():
    frappe.form_dict.cmd = "tenants_manager.api.business.get_keywords"
    frappe.form_dict.keyword_type = "Atmosphere"
    return frappe.handler.handle()

def get_specialties_keywords():
    frappe.form_dict.cmd = "tenants_manager.api.business.get_keywords"
    frappe.form_dict.keyword_type = "Specialties"
    return frappe.handler.handle()

def get_uniqueness_keywords():
    frappe.form_dict.cmd = "tenants_manager.api.business.get_keywords"
    frappe.form_dict.keyword_type = "Uniqueness"
    return frappe.handler.handle()


def get_all_business_for_owner(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.get_all_business_for_owner"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def get_business_details_for_owner(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.get_business_details_for_owner"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def add_business_for_owner(id: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.add_business_for_owner"
    frappe.form_dict.source_id = id
    return frappe.handler.handle()


def upload_business_logo(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.upload_business_logo"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def add_atmosphere_keywords(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.add_business_keywords"
    frappe.form_dict.keyword_type = "Atmosphere"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def add_specialties_keywords(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.add_business_keywords"
    frappe.form_dict.keyword_type = "Specialties"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def add_uniqueness_keywords(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.add_business_keywords"
    frappe.form_dict.keyword_type = "Uniqueness"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def get_atmosphere_keywords(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.get_business_keywords"
    frappe.form_dict.keyword_type = "Atmosphere"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def get_specialties_keywords(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.get_business_keywords"
    frappe.form_dict.keyword_type = "Specialties"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def get_uniqueness_keywords(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.business.get_business_keywords"
    frappe.form_dict.keyword_type = "Uniqueness"
    frappe.form_dict.source_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()


def upload_menus(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.upload_menus_to_s3"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()


def delete_menu(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.delete_menu_from_s3"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()


def parse_menus(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.parse_menus"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()


def menu_upload_group_status():
    frappe.form_dict.cmd = "tenants_manager.api.menu.menu_upload_group_status"
    return frappe.handler.handle()


def create_business_promo():
    frappe.form_dict.cmd = "tenants_manager.api.business_setup.business_promo"
    return frappe.handler.handle()

def is_domain_available():
    frappe.form_dict.cmd = "tenants_manager.api.business.is_domain_available"
    return frappe.handler.handle()

def get_menu_items(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.get_menu_items"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def create_update_menu_items(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.create_update_menu_items"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def delete_menu_items(id: str, bid: str, menu_item_id: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.delete_menu_items"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    frappe.form_dict.menu_item_id = menu_item_id
    return frappe.handler.handle()

def get_menu_categories(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.get_menu_categories"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def create_update_menu_categories(id: str, bid: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.create_update_menu_categories"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    return frappe.handler.handle()

def delete_menu_categories(id: str, bid: str, category_id: str):
    frappe.form_dict.cmd = "tenants_manager.api.menu.delete_menu_categories"
    frappe.form_dict.business_owner_id = id
    frappe.form_dict.business_id = bid
    frappe.form_dict.category_id = category_id
    return frappe.handler.handle()

routes = [
    Rule("/business/atmosphere-keywords", methods=["GET"], endpoint=get_atmosphere_keywords),
    Rule("/business/specialties-keywords", methods=["GET"], endpoint=get_specialties_keywords),
    Rule("/business/uniqueness-keywords", methods=["GET"], endpoint=get_uniqueness_keywords),
    Rule(
        "/business/<path:id>/all-business",
        methods=["GET"],
        endpoint=get_all_business_for_owner,
    ),
    Rule(
        "/business/<path:id>/business-details",
        methods=["GET"],
        endpoint=get_business_details_for_owner,
    ),
    Rule(
        "/business/<path:id>/add-business",
        methods=["POST"],
        endpoint=add_business_for_owner,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/add-logo",
        methods=["PUT"],
        endpoint=upload_business_logo,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/add-atmosphere-keywords",
        methods=["PUT"],
        endpoint=add_atmosphere_keywords,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/add-specialties-keywords",
        methods=["PUT"],
        endpoint=add_specialties_keywords,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/add-uniqueness-keywords",
        methods=["PUT"],
        endpoint=add_uniqueness_keywords,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/atmosphere-keywords",
        methods=["GET"],
        endpoint=get_atmosphere_keywords,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/specialties-keywords",
        methods=["GET"],
        endpoint=get_specialties_keywords,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/uniqueness-keywords",
        methods=["GET"],
        endpoint=get_uniqueness_keywords,
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/upload-menus",
        methods=["POST"],
        endpoint=upload_menus
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/delete-menu",
        methods=["DELETE"],
        endpoint=delete_menu
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/parse-menus",
        methods=["POST"],
        endpoint=parse_menus
    ),
    Rule(
        "/business/menu-upload-group-status",
        methods=["GET"],
        endpoint=menu_upload_group_status
    ),
    Rule(
        "/business/business-promo",
        methods=["GET"],
        endpoint=create_business_promo
    ),
    Rule(
        "/business/is-domain-available",
        methods=["GET"],
        endpoint=is_domain_available
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/menu-items",
        methods=["GET"],
        endpoint=get_menu_items
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/menu-items",
        methods=["POST"],
        endpoint=create_update_menu_items
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/menu-items/<path:menu_item_id>",
        methods=["DELETE"],
        endpoint=delete_menu_items
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/menu-categories",
        methods=["GET"],
        endpoint=get_menu_categories
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/menu-categories",
        methods=["POST"],
        endpoint=create_update_menu_categories
    ),
    Rule(
        "/business/<path:id>/business-details/<path:bid>/menu-categories/<path:category_id>",
        methods=["DELETE"],
        endpoint=delete_menu_categories
    ),
]
