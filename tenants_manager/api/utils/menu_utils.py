import os
import io
import json
import frappe
import base64
from frappe.utils import now
from pdf2image import convert_from_bytes
from spire.doc import Document, ImageType
from PIL import Image


doc_extensions = [".doc", ".docx", ".docm"]
pdf_extensions = [".pdf"]
image_extensions = [".jpg", ".jpeg", ".png"]


def encode_image(file_or_image):
    if isinstance(file_or_image, Image.Image):
        # Handle image
        buffered = io.BytesIO()
        file_or_image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    else:
        # Handle file
        file_data = file_or_image.read()
        return base64.b64encode(file_data).decode('utf-8')

def save_menu_items(menu_id, items_data, business_owner_id, business_id):
    for item in items_data['items']:
        category = item.get("category", "other").lower()
        category_id = frappe.db.exists(
            "Menu Category",
            {
                "category": category,
                "business_owner_id": business_owner_id,
                "business_id": business_id
            }
        )
        if not category_id:
            menu_category_doc = frappe.get_doc({
                "doctype": "Menu Category",
                "category": category,
                "business_owner_id": business_owner_id,
                "business_id": business_id
            })
            menu_category_doc.flags.ignore_permissions = True
            menu_category_doc.insert()
            category_id = menu_category_doc.name

        menu_item_doc = frappe.get_doc({
            "doctype": "Menu Item",
            "category_id": category_id,
            "title": item.get("title") or None,
            "price": convert_to_float(item.get("price")),
            "currency": item.get("currency") or None,
            "description": item.get("description") or None,
            "calories": item.get("calories") or None,
            "menu_id": menu_id,
            "business_owner_id": business_owner_id,
            "business_id": business_id
        })
        ingredients = item.get("ingredients")
        if ingredients and isinstance(ingredients, list):
            for ingredient in ingredients:
                if ingredient:
                    menu_item_doc.append("ingredients", {"ingredient_name": ingredient})

        allergies = item.get("allergies")
        if allergies and isinstance(allergies, list):
            for allergen in allergies:
                if allergen:
                    menu_item_doc.append("allergies", {"allergen_name": allergen})

        variations = item.get("variations")
        if variations and isinstance(variations, list):
            for variation in variations:
                if variation:
                    variation["price"] = convert_to_float(variation.get("price"))
                    menu_item_doc.append("variations", variation)

        menu_item_doc.flags.ignore_permissions = True
        menu_item_doc.insert()
    frappe.db.commit()

def get_singles_value(doctype, field):
    single_value = frappe.db.get_singles_value(doctype, field)
    return single_value

def get_file_extension(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext

def convert_pdf_to_base64_images(pdf_file):
    images = convert_from_bytes(pdf_file.read())
    base64_images = [encode_image(image) for image in images]
    return base64_images

def convert_doc_to_base64_images(doc_file):
    base64_images = []
    file_obj = io.BytesIO(doc_file.read())
    document = Document()
    document.LoadFromStream(file_obj)
    for i in range(document.GetPageCount()):
        imageStream = document.SaveImageToStreams(i, ImageType.Bitmap)
        image_file_obj = io.BytesIO(imageStream.ToArray())
        base64_image = encode_image(image_file_obj)
        base64_images.append(base64_image)
    document.Close()
    return base64_images

def convert_to_float(obj: str):
    try:
        float_obj = float(obj)
    except:
        float_obj = None
    return float_obj
