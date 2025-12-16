# Copyright (c) 2025, opinov8 and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BusinessSiteSecurity(Document):

    @frappe.whitelist()
    def get_admin_password(self):
        # TODO check current user password
        return self.get_password(fieldname="administrator_password")

    @frappe.whitelist()
    def get_support_password(self):
        # TODO check current user password
        return self.get_password(fieldname="support_password")
