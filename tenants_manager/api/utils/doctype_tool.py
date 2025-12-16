import copy
import json

import frappe
from enum import Enum

from frappe.query_builder.functions import GroupConcat, Concat
from frappe import qb
from pypika import CustomFunction
from pypika.functions import DistinctOptionFunction

from tenants_manager.api.utils import build_error_response


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    SUCCESS = "success"


class DoctypeTool:

    def __init__(self, doc=None, doctype=None):
        self.doc = doc
        self.doctype = doctype

    def set_status(self, status: Status):
        if not self.doc:
            frappe.throw(f"Document is not provided")

        if not hasattr(self.doc, "status"):
            frappe.throw(f"Document {self.doc.doctype} does not have a status field")

        try:
            self.doc.status = status.value
            self.doc.flags.ignore_permissions = True
            self.doc.save()
            frappe.db.commit()
        except Exception as e:
            frappe.throw(f"An error occurred while updating {self.doc.doctype} {self.doc.name} status: {e}")

    def get_group_overall_status(self, statuses: list):
        if all(status == Status.SUCCESS.value for status in statuses):
            return Status.SUCCESS.value

        if Status.FAILED.value in statuses:
            return Status.FAILED.value

        if all(status == Status.PENDING.value for status in statuses):
            return Status.PENDING.value

        if Status.IN_PROGRESS.value in statuses:
            return Status.IN_PROGRESS.value

    def get_menu_items(
            self,
            business_owner_id: str = None,
            business_id: str = None,
            menu_upload_group_id: str = None,
            menu_item_id: str = None,
            category_id: str = None
    ):
        def json_arrayagg_distinct(field):
            return DistinctOptionFunction("JSON_ARRAYAGG", field).distinct()
        json_object = CustomFunction("JSON_OBJECT", ["key", "value", "key", "value"])

        menu = qb.DocType("Menu")
        menu_item = qb.DocType("Menu Item")
        menu_category = qb.DocType("Menu Category")
        ingredient = qb.DocType("Ingredient")
        allergen = qb.DocType("Allergen")
        variation = qb.DocType("Variation")

        query = (
            qb.from_(menu_item)
            .inner_join(menu_category).on(menu_category.name == menu_item.category_id)
            .left_join(ingredient).on(ingredient.parent == menu_item.name)
            .left_join(allergen).on(allergen.parent == menu_item.name)
            .left_join(variation).on(variation.parent == menu_item.name)
            .select(
                menu_category.name.as_("category_id"),
                menu_item.name.as_("id"),
                menu_item.title,
                menu_item.image_url,
                menu_item.price,
                menu_item.currency,
                menu_item.description,
                menu_item.calories,
                json_arrayagg_distinct(ingredient.ingredient_name).as_("ingredients"),
                json_arrayagg_distinct(allergen.allergen_name).as_("allergies"),
                Concat(
                    "[",
                    GroupConcat(
                        json_object(
                            "name", variation.variation_name,
                            "price", variation.price
                        )
                    ).distinct(),
                    "]"
                ).as_("variations")
            )
            .where(menu_item.business_owner_id == business_owner_id)
            .where(menu_item.business_id == business_id)
            .groupby(menu_category.name, menu_item.name)
            .orderby(menu_item.creation)
        )

        if menu_upload_group_id:
            query = (
                query
                .inner_join(menu).on(menu.name == menu_item.menu_id)
                .where(menu.menu_upload_group_id == menu_upload_group_id)
            )

        if menu_item_id:
            query = query.where(menu_item.name == menu_item_id)

        if category_id:
            query = query.where(menu_category.name == category_id)

        results = query.run(as_dict=True)

        category_results = dict()

        for item in results:
            ingredients = json.loads(item["ingredients"])
            item["ingredients"] = ingredients if ingredients != [None] else []
            allergies = json.loads(item["allergies"])
            item["allergies"] = allergies if allergies != [None] else []
            variations = json.loads(item["variations"])
            filtered_variations = [variation for variation in variations if None not in variation.values()]
            item["variations"] = filtered_variations

            category_id = item.pop("category_id")
            category_results.setdefault(category_id, []).append(item)

        return {"categories": category_results}

    def validate_data_fields_against_doctype_fields(self, data: dict):
        if not self.doctype:
            frappe.throw(f"Doctype name is not provided")
        meta = frappe.get_meta(self.doctype)

        for fieldname, value in data.items():
            if not meta.has_field(fieldname):
                frappe.throw(f"Field '{fieldname}' is not a valid field for {self.doctype}")
            field_meta = meta.get_field(fieldname)

            # Check for required fields
            if field_meta.reqd and not value:
                frappe.throw(f"Field '{fieldname}' is required for {self.doctype}")

            # Validate data type
            self.validate_field_type(value, field_meta)

    def validate_field_type(self, value, field_meta):
        field_type = field_meta.fieldtype

        if field_type in ["Int", "Check"] and not isinstance(value, int):
            frappe.throw( f"Field '{field_meta.label}' must be an integer")
        if field_type in ["Float", "Currency", "Percent"] and not isinstance(value, (int, float)):
            frappe.throw(f"Field '{field_meta.label}' must be a number")
        if field_type in ["Data", "Small Text", "Text", "Long Text"] and not isinstance(value, str):
            frappe.throw(f"Field '{field_meta.label}' must be a string")
        if field_type == "Link":
            link_doctype = field_meta.options
            if not frappe.db.exists(link_doctype, value):
                frappe.throw(
                    f"Field '{field_meta.label}' must be a valid {link_doctype}. "
                    f"The value '{value}' does not exist in {link_doctype}."
                )

    def create_document(self, data: dict):
        try:
            new_doc = frappe.get_doc({
                "doctype": self.doctype,
                **data
            })
            new_doc.insert()
            frappe.db.commit()
            return new_doc.name
        except Exception as e:
            frappe.throw( f"Failed to create {self.doctype} document with data: {data}. "
                          f"Error ({type(e)}): {e}", RuntimeError)


    def update_document(self, doc_id, data: dict):
        if not frappe.db.exists(self.doctype, doc_id):
            frappe.throw(f"{self.doctype} with ID '{doc_id}' does not exist", frappe.DoesNotExistError)
        try:
            doc = frappe.get_doc(self.doctype, doc_id)
            for field, value in data.items():
                setattr(doc, field, value)
            doc.save()
            frappe.db.commit()
        except Exception as e:
            frappe.throw(
                f"Failed to update {self.doctype} document with ID '{doc_id}'. "
                f"Update data: {data}. Error ({type(e)}): {e}",
                RuntimeError
            )

    def delete_document(self, doc_id):
        if not frappe.db.exists(self.doctype, doc_id):
            frappe.throw(f"{self.doctype} with ID '{doc_id}' does not exist", frappe.DoesNotExistError)
        try:
            frappe.delete_doc(self.doctype, doc_id)
        except Exception as e:
            frappe.throw(
                f"Failed to delete {self.doctype} document with ID '{doc_id}'. Error ({type(e)}): {e}",
                RuntimeError
            )

    def get_doctype_field_values_data(self, field, filters: dict = None):
        doctype_field_values = frappe.get_all(self.doctype, fields=["name", field], filters=filters)
        values_data = [
            {
                "id": field_value["name"],
                field: field_value[field]
            }
            for field_value in doctype_field_values
        ]
        return values_data

    def get_doc_visible_data(self, doc):
        meta = frappe.get_meta(self.doctype)
        visible_fields = [field.fieldname for field in meta.get_visible_fields()]
        visible_data = {field: doc.get(field) for field in visible_fields}
        return visible_data


class MenuItemTool(DoctypeTool):
    def __init__(self, business_owner_id, business_id):
        super().__init__(doctype="Menu Item")
        self.business_owner_id = business_owner_id
        self.business_id = business_id

    def create(self, data: dict):
        item_data = copy.deepcopy(data)
        ingredients = item_data.pop('ingredients', [])
        allergies = item_data.pop('allergies', [])
        variations = item_data.pop('variations', [])

        try:
            new_doc = frappe.get_doc({
                "doctype": self.doctype,
                "business_owner_id": self.business_owner_id,
                "business_id": self.business_id,
                **item_data
            })
            for ingredient in ingredients:
                new_doc.append("ingredients", {"ingredient_name": ingredient})

            for allergen in allergies:
                new_doc.append("allergies", {"allergen_name": allergen})

            for variation in variations:
                new_doc.append("variations", {
                    "variation_name": variation.get("name"),
                    "price": variation.get("price")
                })

            new_doc.insert()
            frappe.db.commit()
            return new_doc.name
        except Exception as e:
            frappe.throw(
                f"Failed to create {self.doctype} document with data: {data}. Error ({type(e)}): {e}",
                RuntimeError
            )


    def update(self, doc_id, data):
        if not frappe.db.exists(self.doctype, doc_id):
            frappe.throw(f"{self.doctype} with ID '{doc_id}' does not exist", frappe.DoesNotExistError)
        ingredients = data.pop("ingredients", [])
        allergies = data.pop("allergies", [])
        variations = data.pop("variations", [])
        data["business_owner_id"] = self.business_owner_id
        data["business_id"] = self.business_id
        try:
            menu_item_doc = frappe.get_doc(self.doctype, doc_id)
            for field, value in data.items():
                setattr(menu_item_doc, field, value)

            for ingredient in ingredients:
                menu_item_doc.append("ingredients", {"ingredient_name": ingredient})

            for allergen in allergies:
                menu_item_doc.append("allergies", {"allergen_name": allergen})

            for variation in variations:
                menu_item_doc.append("variations", {
                    "variation_name": variation.get("name"),
                    "price": variation.get("price")
                })

            menu_item_doc.save()
            frappe.db.commit()
        except Exception as e:
            frappe.throw(
                f"Failed to update {self.doctype} document with ID '{doc_id}'. Update data: {data}. "
                f"Error ({type(e)}): {e}",
                RuntimeError
            )
