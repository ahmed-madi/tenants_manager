import json
import frappe
from openai import OpenAI

from tenants_manager.api.utils.aws_tool import secrets_manager
from tenants_manager.api.utils.openai_content import parse_menu_text


class OpenaiTool:

    def __init__(self):
        self.openai_api_key = secrets_manager.get("openai_api_key")
        if not self.openai_api_key:
            return frappe.throw("openai_api_key not provided in secrets manager", frappe.MandatoryError)
        self.client = OpenAI(api_key=self.openai_api_key)

    def parse_menu_image(self, base64_image: str):
        request_content = [{
            "type": "text",
            "text": parse_menu_text
        }]
        request_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": request_content,
                }
            ],
        )
        parsed_data = response.choices[0].message.content
        parsed_data = parsed_data.strip('```json').strip('```')
        try:
            parsed_data = json.loads(parsed_data)
            return parsed_data
        except Exception:
            parsed_data = self.get_valid_json(parsed_data)

        parsed_data = parsed_data.strip('```json').strip('```')
        try:
            parsed_data = json.loads(parsed_data)
        except Exception:
            frappe.throw(f"Failed to get JSON object from string: {parsed_data}")

        return parsed_data

    def create_business_promo(self, key_words: str):
        text_content = f"""
                    We have list of words which describe our food establishment: {key_words}. 
                    Write food establishment promotional description based on provided list.
                    Do not specify the food establishment type. Use emotional language and appeal to emotions.
                    Provide couple sentences. Up to 40 words.
                """
        promo = self.text_request(text_content)
        return promo

    def text_request(self, text_content: str):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": text_content
                }
            ]
        )
        text_response = response.choices[0].message.content
        return text_response

    def get_valid_json(self, json_string):
        text_content = f"""
                    Modify provided string to have a valid json strusture: {json_string}. 
                    We need that this string could be passed to the method json.loads().
                    Return valid json string in one line without line breaks.
                """
        modified_json_string = self.text_request(text_content)
        return modified_json_string



openai_tool = OpenaiTool()
