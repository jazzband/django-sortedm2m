if (jQuery === undefined) {
    jQuery = django.jQuery;
}

(function ($) {
    $(function () {
        $('.sortedm2m-container').find('ul').addClass('hide');
        function prepareUl(ul) {
            ul.addClass('sortedm2m');
            var checkboxes = ul.find('input[type=checkbox]');
            var id = checkboxes.first().attr('id').match(/^(.*)_\d+$/)[1];
            var name = checkboxes.first().attr('name');
            checkboxes.removeAttr('name');
            ul.before('<input type="hidden" id="' + id + '" name="' + name + '" />');
            var recalculate_value = function () {
                var values = [];
                ul.find(':checked').each(function () {
                    values.push($(this).val());
                });
                $('#' + id).val(values.join(','));
            };
            recalculate_value();
            ul.on('change','input[type=checkbox]',recalculate_value);
            ul.sortable({
                axis: 'y',
                //containment: 'parent',
                update: recalculate_value
            });
            return ul;
        }

        function iterateUl() {
            $('ul:has(.sortedm2m)').each(function () {
                prepareUl( $(this) );
                $(this).removeClass('hide');
            });
        }

        $(".add-row a").click(iterateUl);

        iterateUl();

        $('.sortedm2m-container .selector-filter input').each(function () {
            $(this).bind('input', function() {
                var search = $(this).val().toLowerCase();
                var $el = $(this).closest('.selector-filter');
                var $container = $el.siblings('ul').each(function() {
                    // walk over each child list el and do name comparisons
                    $(this).children().each(function() {
                        var curr = $(this).find('label').text().toLowerCase();
                        if (curr.indexOf(search) === -1) {
                            $(this).css('display', 'none');
                        } else {
                            $(this).css('display', 'inherit');
                        }
                    });
                });
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
