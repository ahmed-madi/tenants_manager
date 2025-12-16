import frappe

from tenants_manager.api.utils.openai_tool import OpenaiTool
from tenants_manager.api.utils.response import build_response


@frappe.whitelist(methods=["GET"])
def business_promo(words: str):
    openai_tool = OpenaiTool()
    promo_text = openai_tool.create_business_promo(words)
    build_response(promo_text, "Business promo is created")
