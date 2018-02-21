$( document ).ready(function() {
    $(".month").bind("click", function() {
        $("input[type='checkbox']").prop({
            disabled: false
        });
    });
});