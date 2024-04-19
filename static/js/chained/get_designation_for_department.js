var result = {};
function get_designation_for_department(department_id) {
    (function ($) {
        var selected_value = $("#id_designation").val();

        $.getJSON("helper/get_designation_for_department", { department_id: department_id }, function (res, textStatus) {
            var options = '<option value="" selected="selected">---------</option>';
            $.each(res.data, function (i, item) {
                options += '<option value="' + item.id + '">' + item.name + '</option>';
            });
            result[department_id] = options;
            $("#id_designation").html(result[department_id]);
            $("select#id_designation option").each(function () {
                if ($(this).val() == selected_value)
                    $(this).attr("selected", "selected");
            });
        });
    })(jQuery);
}