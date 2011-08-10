/* Tab to next input on Enter */
jQuery(document).ready(function(){
    function FormHandler() {
        var submitted_by_enter = false;
        this.onKeyDown = function(event) {
            if (event.keyCode == 13) {
                submitted_by_enter = true;
            }
        };
        this.onKeyUp = function(event) {
            if (event.keyCode == 13) {
                if (submitted_by_enter) {
                    var inputs = jQuery(this).closest('form').find(':input:visible');
                    inputs.eq(inputs.index(this) + 1).focus();
                    submitted_by_enter = false;
                }
            }
        };
        this.onSubmit = function(event) {
            if (submitted_by_enter) {
                return false;
            }
            return true;
        }
    };

    var _form_handler = new FormHandler();
    jQuery('form').submit(_form_handler.onSubmit);
    jQuery('input:not(:submit):not(:button):not(:reset)')
        .keydown(_form_handler.onKeyDown)
        .keyup(_form_handler.onKeyUp);
});
