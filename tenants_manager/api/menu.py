import frappe
import uuid

from tenants_manager.api.utils import check_existence
from tenants_manager.api.utils.response import build_response, build_error_response
from tenants_manager.api.utils.aws_tool import S3bucket, BusinessOwnerMenuS3bucket
from tenants_manager.api.utils.doctype_tool import DoctypeTool, Status, MenuItemTool

from tenants_manager.api.utils.openai_tool import openai_tool
from tenants_manager.api.utils.menu_utils import (
    encode_image,
    get_file_extension,
    convert_pdf_to_base64_images, save_menu_items, doc_extensions, pdf_extensions, image_extensions,
    convert_doc_to_base64_images
)



@frappe.whitelist(methods=["POST"])
def upload_menus_to_s3(business_owner_id: str = None, business_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    uploaded_files = frappe.request.files.getlist('file')
    if not uploaded_files:
        frappe.throw("File is required", frappe.MandatoryError)

    menu_upload_group_doc = frappe.get_doc({
        "doctype": "Menu Upload Group",
        "business_owner_id": business_owner_id,
        "business_id": business_id,
        "status": Status.PENDING.value
    })
    menu_upload_group_doc.flags.ignore_permissions = True
    menu_upload_group_doc.insert()

    for uploaded_file in uploaded_files:
        s3_file_path = BusinessOwnerMenuS3bucket(business_owner_id, business_id).upload_menu(uploaded_file)
        file_name = s3_file_path.split('/')[-1]

        menu_doc = frappe.get_doc({
            "doctype": "Menu",
            "file_name": file_name,
            "file_path": s3_file_path,
            "status": Status.PENDING.value,
            "menu_upload_group_id": menu_upload_group_doc.name
        })
        menu_doc.flags.ignore_permissions = True
        menu_doc.insert()

    frappe.db.commit()

    build_response({"menu_upload_group_id": menu_upload_group_doc.name}, "File(s) uploaded successfully")


@frappe.whitelist(methods=["DELETE"])
def delete_menu_from_s3(business_owner_id: str = None, business_id: str = None, menu_name: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    BusinessOwnerMenuS3bucket(business_owner_id, business_id).delete_menu(menu_name)
    build_response(f"Deleted menu: {menu_name}", "Menu deleted successfully")


@frappe.whitelist(methods=["GET"])
def get_menu_items(
        business_owner_id: str = None,
        business_id: str = None,
        menu_upload_group_id: str = None,
        menu_item_id: str = None,
        category_id: str = None
):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    if category_id:
        if not frappe.db.exists("Menu Category", category_id):
            return build_error_response("NOT_FOUND", f"Provided '{category_id}' category_id doesn't exist")

    menu_items = DoctypeTool().get_menu_items(
        business_owner_id=business_owner_id,
        business_id=business_id,
        menu_upload_group_id=menu_upload_group_id,
        menu_item_id=menu_item_id,
        category_id=category_id
    )
    build_response(menu_items, "Menu items retrieved successfully")


@frappe.whitelist(methods=["POST"])
def create_update_menu_items(business_owner_id: str = None, business_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    data = frappe.request.form.get('data')
    image = frappe.request.files.get('image')

    data = frappe.parse_json(data)
    menu_item_id = data.pop("menu_item_id", None)

    menu_item_tool = MenuItemTool(business_owner_id, business_id)
    menu_item_tool.validate_data_fields_against_doctype_fields(data)

    s3_file_url= BusinessOwnerMenuS3bucket(business_owner_id, business_id).upload_menu_item(image)
    data["image_url"] = s3_file_url

    if menu_item_id:
        menu_item_tool.update(doc_id=menu_item_id, data=data)
        build_response(
            f"Successfully updated '{menu_item_id}' Menu Item",
            "Successfully updated menu item"
        )
    else:
        new_menu_item_id = menu_item_tool.create(data=data)
        build_response(
            {"menu_item_id": new_menu_item_id},
            f"Successfully created '{new_menu_item_id}' Menu Item",
            status_code = 201
        )


@frappe.whitelist(methods=["DELETE"])
def delete_menu_items(business_owner_id: str = None, business_id: str = None, menu_item_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    mi_name = check_existence("Menu Item", menu_item_id)
    if not mi_name:
        return

    menu_item_tool = MenuItemTool(business_owner_id, business_id)
    menu_item_tool.delete_document(doc_id=menu_item_id)
    build_response(
        f"Successfully deleted '{menu_item_id}' Menu Item",
        "Successfully deleted menu item"
    )


@frappe.whitelist(methods=["GET"])
def get_menu_categories(business_owner_id: str = None, business_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    category_tool = DoctypeTool(doctype="Menu Category")
    categories_data = category_tool.get_doctype_field_values_data(
        "category",
        {"business_owner_id": business_owner_id, "business_id": business_id}
    )
    build_response(categories_data, "Menu categories retrieved successfully")


@frappe.whitelist(methods=["POST"])
def create_update_menu_categories(business_owner_id: str = None, business_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    data = frappe.form_dict
    data.pop('cmd', None)
    category_id = data.pop("category_id", None)
    data["category"] = data["category"].lower()

    category_tool = DoctypeTool(doctype="Menu Category")
    category_tool.validate_data_fields_against_doctype_fields(data)

    if category_id:
        category_tool.update_document(doc_id=category_id, data=data)
        build_response(
            f"Successfully updated '{category_id}' Menu Category",
            "Successfully updated menu category"
        )
    else:
        new_menu_category_id = category_tool.create_document(data=data)
        build_response(
            {"category_id": new_menu_category_id},
            f"Successfully created '{new_menu_category_id}' Menu Category",
            status_code=201
        )


@frappe.whitelist(methods=["DELETE"])
def delete_menu_categories(business_owner_id: str = None, business_id: str = None, category_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    c_name = check_existence("Menu Category", category_id)
    if not c_name:
        return

    category_tool = DoctypeTool(doctype="Menu Category")
    category_tool.delete_document(doc_id=category_id)
    build_response(
        {"category_id": category_id},
        f"Successfully deleted '{category_id}' Menu Category"
    )


@frappe.whitelist(methods=["POST"])
def parse_menus(business_owner_id: str = None, business_id: str = None, menu_upload_group_id: str = None):
    name = check_existence("Business Owner", business_owner_id)
    if not name:
        return

    b_name = check_existence("Business", business_id)
    if not b_name:
        return

    if not menu_upload_group_id:
        frappe.throw("menu_upload_group_id parameter is required", frappe.MandatoryError)

    mug_name = check_existence("Menu Upload Group", menu_upload_group_id)
    if not mug_name:
        return

    menu_upload_group_doc = frappe.get_doc("Menu Upload Group", menu_upload_group_id)
    DoctypeTool(menu_upload_group_doc).set_status(Status.IN_PROGRESS)

    menus = frappe.get_all("Menu", {"menu_upload_group_id": menu_upload_group_id})

    if not menus:
        frappe.throw(f"No menus found for menu_upload_group_id {menu_upload_group_id}", frappe.DoesNotExistError)

    for menu in menus:
        menu_doc = frappe.get_doc("Menu", menu["name"])
        frappe.enqueue(
            process_menu,
            timeout=600,
            menu=menu_doc,
            business_owner_id=business_owner_id,
            business_id=business_id
        )
        # process_menu(
        #     menu_doc,
        #     business_owner_id=business_owner_id,
        #     business_id=business_id
        # )

    build_response({"menu_upload_group_id": menu_upload_group_id}, "Menus data is parsed")


@frappe.whitelist(methods=["GET"])
def menu_upload_group_status(menu_upload_group_id: str = None):
    if not menu_upload_group_id:
        frappe.throw("menu_upload_group_id parameter is required", frappe.MandatoryError)

    upload_group_menus = frappe.get_all(
        "Menu",
        filters = {"menu_upload_group_id": menu_upload_group_id},
        fields = ["status"]
    )
    if not upload_group_menus:
        frappe.throw(
            f"No Menu Upload Group documents found for menu_upload_group_id {menu_upload_group_id}",
            frappe.DoesNotExistError
        )

    statuses = [item["status"] for item in upload_group_menus]
    group_overall_status = DoctypeTool().get_group_overall_status(statuses)

    menu_upload_group_doc = frappe.get_doc("Menu Upload Group", menu_upload_group_id)
    menu_upload_group_doc.status = group_overall_status
    menu_upload_group_doc.flags.ignore_permissions = True
    menu_upload_group_doc.save()
    frappe.db.commit()

    build_response({"status": group_overall_status}, "Menu upload group status")


def process_menu(menu, business_owner_id, business_id):
    menu_tool = DoctypeTool(menu)
    menu_tool.set_status(Status.IN_PROGRESS)

    menu_full_path = menu.get("file_path")
    menu_path = "/".join(menu_full_path.split("/")[1:])
    menu_file = S3bucket().get_file(menu_path)
    menu_extension = get_file_extension(menu_path)
    if menu_extension in doc_extensions:
        base64_images = convert_doc_to_base64_images(menu_file)
    elif menu_extension in pdf_extensions:
        base64_images = convert_pdf_to_base64_images(menu_file)
    elif menu_extension in image_extensions:
        base64_images = [encode_image(menu_file)]
    else:
        frappe.throw(f"Unsupported file extension: {menu_extension}. " 
                     f"Supported extensions are: {', '.join([*doc_extensions, *pdf_extensions, *image_extensions])}")

    try:
        for base64_image in base64_images:
            parsed_data = openai_tool.parse_menu_image(base64_image)

            save_menu_items(menu.name, parsed_data, business_owner_id, business_id)

        menu_tool.set_status(Status.SUCCESS)
    except Exception as e:
        menu_tool.set_status(Status.FAILED)
        menu_upload_group_id = menu.get("menu_upload_group_id")
        menu_upload_group_doc = frappe.get_doc("Menu Upload Group", menu_upload_group_id)
        DoctypeTool(menu_upload_group_doc).set_status(Status.FAILED)
        frappe.throw("Failed to process the menu photo.")
