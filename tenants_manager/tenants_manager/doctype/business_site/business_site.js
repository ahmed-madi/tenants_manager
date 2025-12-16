// Copyright (c) 2025, opinov8 and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Site", {
    refresh(frm) {
        if (frm.doc.docstatus != 1) {
            return;
        }
        if (frm.doc.status === "Pending") {
            frm.add_custom_button(__("Build Site"), () => {
                frappe.call({
                    method: "create_site",
                    doc: frm.doc,
                    callback: function (r) {
                        frm.reload_doc();
                        console.log("+____");
                    },
                });
            });
        } else if (frm.doc.status === "Ready to Use") {
            frm.add_custom_button(__("Stop Site"), () => { });
            frm.add_custom_button(__("Suspend Site"), () => { });
        } else if (frm.doc.status === "Failed") {
            frm.add_custom_button(__("Re-Build Site"), () => {
                frappe.call({
                    method: "create_site",
                    doc: frm.doc,
                    callback: function (r) {
                        frm.reload_doc();
                        console.log("+____1");
                    },
                });
            });
        } else if (frm.doc.status === "Suspended") {
            frm.add_custom_button(__("Start Site"), () => { });
        }
    },
});
