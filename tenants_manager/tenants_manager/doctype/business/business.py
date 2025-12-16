# Copyright (c) 2025, opinov8 and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class Business(Document):
    def validate(self):
        self.domain_name = self.business_name.replace(" ", "-").lower()

    def after_insert(self):
        self.db_set("status", "Completed")
        if (
            cint(
                frappe.db.get_single_value(
                    "Business Site Settings", "auto_create_site_after_submit_business"
                )
            )
            == 0
        ):
            return
        site = frappe.new_doc("Business Site")
        site.business_owner = self.business_owner
        site.business = self.name
        site.save(ignore_permissions=True)
        site.submit()

        site.create_site()

    def on_cancel(self):
        self.db_set("status", "Cancelled")
