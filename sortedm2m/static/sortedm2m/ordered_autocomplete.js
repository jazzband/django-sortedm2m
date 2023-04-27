'use strict';
{
    const $ = django.jQuery;

    $.fn.djangoAdminSelect2 = function() {
        $.each(this, function(i, element) {
            $(element).select2({
                ajax: {
                    data: (params) => {
                        return {
                            term: params.term,
                            page: params.page,
                            app_label: element.dataset.appLabel,
                            model_name: element.dataset.modelName,
                            field_name: element.dataset.fieldName
                        };
                    }
                }
            });
            let select = $('select#' + element.getAttribute('id'));
            let children = select.next().children().children().children();
            children.sortable({
                containment: 'parent',
                stop: function (event, ui) {
                    ui.item.parent().children('[title]').each(function () {
                        let title = $(this).attr('title');
                        let original = $('option:contains(' + title + ')', select).first();
                        original.detach();
                        select.append(original)
                    });
                    select.change();
                }
            });
        });
        return this;
    };

    $(function() {
        // Initialize all autocomplete widgets except the one in the template
        // form used when a new formset is added.
        $('.admin-autocomplete').not('[name*=__prefix__]').djangoAdminSelect2();
    });

    document.addEventListener('formset:added', (event) => {
        $(event.target).find('.admin-autocomplete').djangoAdminSelect2();
    });
}





// (function() {
//     setTimeout( function() {
//         let $ = django.jQuery;
//         let selects = $('select.admin-autocomplete')
//         console.log(selects);
//         selects.each(function(index, element) {
//             let select = $(element).select2();
//             let children = select.next().children().children().children();
//             children.sortable({
//                 containment: 'parent',
//                 stop: function (event, ui) {
//                     ui.item.parent().children('[title]').each(function () {
//                         let title = $(this).attr('title');
//                         let original = $('option:contains(' + title + ')', select).first();
//                         original.detach();
//                         select.append(original)
//                     });
//                     select.change();
//                 }
//             });
//         });
//     }, 1000);
// })();