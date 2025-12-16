# Copyright (c) 2025, opinov8 and contributors
# For license information, please see license.txt
from re import match

import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document


class BusinessSiteSettings(Document):
    def validate(self):
        self.validate_domain_name()
        self.validate_oauth()

    def validate_domain_name(self):
        """
        Validate the domain name to ensure it:
        - Does not start with a number or any special character
        - Can contain letters, numbers, dots, underscores, hyphens, and at symbols
        - Does not end with a special character
        """
        if not self.domain:
            return

        regex = r"^(?![0-9\W])(?:[a-zA-Z0-9][a-zA-Z0-9._@-]*[a-zA-Z0-9])?$"

        if not match(regex, self.domain):
            frappe.throw(_("Invalid domain name: <b>{0}</b>").format(self.domain))

    def validate_oauth(self):
        if cint(self.enable_oauth) == 0:
            return
        missing = []
        if not self.oauth_client:
            missing.append("<li>" + _("OAuth Client") + "</li>")
        if len(missing) > 0:
            msg = _("Mandatory fields required in Business Site Settings")
            frappe.throw(
                title=_("Missing Fields"),
                msg=_(msg + "<ul>" + "".join(missing) + "</ul>"),
            )
            return
