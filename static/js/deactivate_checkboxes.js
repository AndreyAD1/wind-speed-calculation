$( document ).ready(function() {
    $(".all_days").bind("click", function() {
        $("input[type='checkbox']").prop({
            disabled: true, checked: false
        });
    });
});