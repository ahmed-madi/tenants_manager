frappe.listview_settings["Business"] = {
  get_indicator: function (doc) {
    var colors = {
      New: "blue",
      "Business Name Added": "yellow",
      "Logo Added": "yellow",
      "Atmosphere Keywords Added": "orange",
      "Specialties Keywords Added": "red",
      "Uniqueness Keywords Added": "green",
      Completed: "green",
      Cancelled: "red",
    };
    return [__(doc.status), colors[doc.status], "status,=," + doc.status];
  },
  hide_name_column: true,
};
