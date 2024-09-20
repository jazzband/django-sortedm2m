from django import forms
from django.conf import settings
from django.utils import translation
from django.contrib.admin.widgets import AutocompleteSelectMultiple

class OrderedAutocomplete(AutocompleteSelectMultiple):
    def optgroups(self, name, value, attr=None):
        """Return selected options based on the ModelChoiceIterator."""
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        # Use a list instead of a set to keep around the order returned
        # by SortedManyToManyField
        selected_choices = [
            str(v) for v in value
            if str(v) not in self.choices.field.empty_values
        ]
        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, "", "", False, 0))
        remote_model_opts = self.field.remote_field.model._meta
        to_field_name = getattr(
            self.field.remote_field, "field_name", remote_model_opts.pk.attname
        )
        to_field_name = remote_model_opts.get_field(to_field_name).attname
        choices = (
            (getattr(obj, to_field_name), self.choices.field.label_from_instance(obj))
            for obj in self.choices.queryset.using(self.db).filter(
                **{"%s__in" % to_field_name: selected_choices}
            )
        )
        # Sort choices according to what is returned by SortedManyToManyField
        choices = list(choices)
        choices.sort(key=lambda x: selected_choices.index(str(x[0])))
        for option_value, option_label in choices:
            selected = str(option_value) in value and (
                has_selected is False or self.allow_multiple_selected
            )
            has_selected |= selected
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(
                self.create_option(
                    name, option_value, option_label, selected_choices, index
                )
            )
        return groups

    class Media:
        extra = "" if settings.DEBUG else ".min"
        lang = translation.get_language()
        js = ( 
            "admin/js/vendor/jquery/jquery%s.js" % extra,
            "admin/js/vendor/select2/select2.full%s.js" % extra,
        ) + (
            "admin/js/vendor/select2/i18n/%s.js" % lang,
        ) + (
            'sortedm2m/jquery-ui.min.js',
            "admin/js/jquery.init.js",
            "sortedm2m/ordered_autocomplete.js"
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2%s.css" % extra,
                "admin/css/autocomplete.css",
                "sortedm2m/ordered_autocomplete.css",
            )
        }


class SortedM2MAutocompleteMixin:

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        using = kwargs.get("using")
        if db_field.name in self.sorted_autocomplete_fields:
            kwargs['widget'] = OrderedAutocomplete(
                db_field,
                self.admin_site,
                using=using
            )
            if 'queryset' not in kwargs:
                queryset = self.get_field_queryset(using, db_field, request)
                if queryset is not None:
                    kwargs['queryset'] = queryset

            form_field = db_field.formfield(**kwargs)
            return form_field

        return super().formfield_for_manytomany(db_field, request, **kwargs)
