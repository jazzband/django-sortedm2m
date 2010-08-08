(function ($) {
    $(function () {
        $('.sortedm2m').parents('ul').each(function () {
            $(this).addClass('sortedm2m');
            var checkboxes = $(this).find('input[type=checkbox]');
            var id = checkboxes.first().attr('id').match(/^(.*)_\d+$/)[1];
            var name = checkboxes.first().attr('name');
            checkboxes.removeAttr('name');
            $(this).before('<input type="hidden" id="' + id + '" name="' + name + '" />');
            var that = this;
            var recalculate_value = function () {
                var values = [];
                $(that).find(':checked').each(function () {
                    values.push($(this).val());
                });
                $('#' + id).val(values.join(','));
            }
            recalculate_value();
            checkboxes.change(recalculate_value);
            $(this).sortable({
                axis: 'y',
                //containment: 'parent',
                update: recalculate_value
            });
        });
    });
})(django.jQuery);
jQuery = django.jQuery;
