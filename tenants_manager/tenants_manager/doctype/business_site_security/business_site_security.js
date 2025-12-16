// Copyright (c) 2025, opinov8 and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Site Security", {
    refresh(frm) {
        frm.add_custom_button(
            __("Admin"),
            function () {
                frappe.call({
                    method: "get_admin_password",
                    doc: frm.doc,
                    freeze: true,
                    callback: function (r) {
                        frappe.msgprint(
                            `Admin password in ${frm.doc.site_name} is <b>${r.message}</b>`
                        );
                    },
                });
            },
            __("Show Password")
        );
        frm.add_custom_button(
            __("Support"),
            function () {
                frappe.call({
                    method: "get_support_password",
                    doc: frm.doc,
                    freeze: true,
                    callback: function (r) {
                        frappe.msgprint(
                            `Support user password in ${frm.doc.site_name} is <b>${r.message}</b>`
                        );
                    },
                });
            },
            __("Show Password")
        );
    },
});
