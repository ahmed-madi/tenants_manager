# Copyright (c) 2025, opinov8 and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BusinessOwner(Document):
    def validate(self):
        self.full_name = f"{self.first_name} {self.last_name}"

    def on_trash(self):
        self.delete_linked_business()
        self.delete_linked_upload_groups()
        frappe.db.commit()
    
    def delete_linked_business(self):
        for v in frappe.db.sql(
            "SELECT name FROM `tabBusiness` WHERE business_owner='{}'".format(self.name)
        ):
            frappe.delete_doc(
                doctype="Business",
                name=v[0],
                force=True,
                ignore_doctypes=["Business Site"],
                ignore_permissions=True,
                ignore_on_trash=True,
                delete_permanently=True,
                for_reload=True,
            )
    def delete_linked_upload_groups(self):
        for v in frappe.db.sql(
            "SELECT name FROM `tabMenu Upload Group` WHERE business_owner_id='{}'".format(self.name)
        ):
            frappe.delete_doc(
                doctype="Menu Upload Group",
                name=v[0],
                force=True,
                ignore_permissions=True,
                ignore_on_trash=True,
                delete_permanently=True,
                for_reload=True,
            )
