if (jQuery === undefined) {
    jQuery = django.jQuery;
}

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

        if (window.showAddAnotherPopup) {
            var django_dismissAddAnotherPopup = window.dismissAddAnotherPopup;
            window.dismissAddAnotherPopup = function (win, newId, newRepr) {
                // newId and newRepr are expected to have previously been escaped by
                // django.utils.html.escape.
                newId = html_unescape(newId);
                newRepr = html_unescape(newRepr);
                var name = windowname_to_id(win.name);
                var elem = $('#' + name);
                var sortedm2m = elem.siblings('ul.sortedm2m');
                if (sortedm2m.length == 0) {
                    // no sortedm2m widget, fall back to django's default
                    // behaviour
                    return django_dismissAddAnotherPopup.apply(this, arguments);
                }

                if (elem.val().length > 0) {
                    elem.val(elem.val() + ',');
                }
                elem.val(elem.val() + newId);

                var id_template = '';
                var maxid = 0;
                sortedm2m.find('li input').each(function () {
                    var match = this.id.match(/^(.+)_(\d+)$/);
                    id_template = match[1];
                    id = parseInt(match[2]);
                    if (id > maxid) maxid = id;
                });

                var id = id_template + '_' + (maxid + 1);
                var new_li = $('<li/>').append(
                    $('<label/>').attr('for', id).append(
                        $('<input class="sortedm2m" type="checkbox" checked="checked" />').attr('id', id).val(newId)
                    ).append($('<span/>').text(' ' + newRepr))
                );
                sortedm2m.append(new_li);

                win.close();
            };
        }
    });
})(jQuery);
