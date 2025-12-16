frappe.listview_settings["Business Site"] = {
    get_indicator: function (doc) {
        var colors = {
            Draft: "gray",
            Pending: "orange",
            "In Progress": "blue",
            "Ready to Use": "green",
            Failed: "red",
            Suspended: "yellow",
            Cancelled: "red",
        };
        return [__(doc.status), colors[doc.status], "status,=," + doc.status];
    },
    hide_name_column: true,
};
