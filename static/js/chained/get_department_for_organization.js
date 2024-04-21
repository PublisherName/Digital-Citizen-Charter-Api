var result = {};
function get_department_for_organization(organization_id) {
    (function ($) {
        var selected_value = $("#id_department").val();

        $.getJSON("/helper/get_department_for_organization", { organization_id: organization_id }, function (res, textStatus) {
            var options = '<option value="" selected="selected">---------</option>';
            $.each(res.data, function (i, item) {
                options += '<option value="' + item.id + '">' + item.name + '</option>';
            });
            result[organization_id] = options;
            $("#id_department").html(result[organization_id]);
            $("select#id_department option").each(function () {
                if ($(this).val() == selected_value)
                    $(this).attr("selected", "selected");
            });
        });
    })(django.jQuery);
}