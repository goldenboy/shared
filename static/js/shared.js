/* Tab to next input on Enter */
jQuery(document).ready(function(){
    function FormHandler() {
        var submitted_by_enter = false;
        this.onKeyDown = function(event) {
            if (event.keyCode == 13) {
                submitted_by_enter = true;
                var inputs = jQuery(this).closest('form').find(':input:visible');
                inputs.eq(inputs.index(this) + 1).focus();
            }
        };
        this.onSubmit = function(event) {
            if (submitted_by_enter) {
                submitted_by_enter = false;
                return false;
            }
            return true;
        }
    };

    var _form_handler = new FormHandler();
    jQuery('form').submit(_form_handler.onSubmit);
    jQuery('input').keydown(_form_handler.onKeyDown);
});
