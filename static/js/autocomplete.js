$( document ).ready(function() {
    $(function() {
        $("#station_id").autocomplete({
            source: function (request, response) {
                 $.ajax({
                     url: "/suggest",
                     type: "GET",
                     data: request,
                         dataType: "JSON",
                         minLength: 1,
                     success: function (data) {
                         response($.map(data, function (el) {
                             return {
                                 label: el.name,
                                 value: el.id
                             };
                         }));
                     }
                 });
            },
            select: function (event, ui) {
                this.value = ui.item.value;
                event.preventDefault();
            }
        });
    });
});