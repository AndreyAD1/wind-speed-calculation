$( document ).ready(function() {
    $.datepicker.setDefaults(
        $.extend(
            {'dateFormat':'dd.mm.yy'},
            $.datepicker.regional['ru']
        )
    );
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
    $( function() {
        var dateFormat = "dd.mm.yy",
        from = $( "#from" )
        .datepicker({
            dateFormat: "dd.mm.yy",
            defaultDate: "+1w",
            minDate: null,
            maxDate: "d",
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 1,
            showOn: "both",
            buttonImage: "/static/img/glyphicons-46-calendar.png",
            buttonImageOnly: true,
            buttonText: "Выберите дату"
        })
        .on( "change", function() {
            to.datepicker( "option", "minDate", getDate( this ) );
        }),
        to = $( "#to" )
        .datepicker({
            dateFormat: "dd.mm.yy",
            defaultDate: "+1w",
            minDate: null,
            maxDate: "d",
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 1,
            showOn: "both",
            buttonImage: "/static/img/glyphicons-46-calendar.png",
            buttonImageOnly: true,
            buttonText: "Выберите дату"
        })
        .on( "change", function() {
            from.datepicker( "option", "maxDate", getDate( this ) );
        });

        function getDate( element ) {
            var date;
            try {
                date = $.datepicker.parseDate( dateFormat, element.value );
            } catch( error ) {
                date = null;
            }

            return date;
        }
    });
});