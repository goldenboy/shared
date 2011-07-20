/* Tab to next input on Enter */
jQuery(document).ready(function(){
    jQuery('input').keydown( function(e) {
            var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
            if(key == 13) {
                e.preventDefault();
                var inputs = jQuery(this).closest('form').find(':input:visible');
                inputs.eq(inputs.index(this) + 1).focus();
            }
    });
});
