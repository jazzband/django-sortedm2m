# -*- coding: utf-8 -*-
from itertools import chain
from django import forms
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


STATIC_URL = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)

class SortedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    class Media:
        js = (
            STATIC_URL + 'sortedm2m/widget.js',
            STATIC_URL + 'sortedm2m/jquery-ui.js',
        )
        css = {'screen': (
            STATIC_URL + 'sortedm2m/smoothness/jquery-ui-1.8.2.custom.css',
            STATIC_URL + 'sortedm2m/widget.css',
        )}

    def build_attrs(self, attrs=None, **kwargs):
        attrs = super(SortedCheckboxSelectMultiple, self).\
            build_attrs(attrs, **kwargs)
        classes = attrs.setdefault('class', '').split()
        classes.append('sortedm2m')
        attrs['class'] = u' '.join(classes)
        return attrs

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        selected_cbs = {}
        unselected_cbs = []
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            html = u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label)
            if option_value in str_values:
                selected_cbs[option_value] = html
            else:
                unselected_cbs.append(html)
        output.extend([selected_cbs[unicode(pk)] for pk in value])
        output.extend(unselected_cbs)
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if value and ',' in value:
            return data[name].split(',')
        if value:
            return value
        return None


class SortedMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = SortedCheckboxSelectMultiple

    def clean(self, value):
        queryset = super(SortedMultipleChoiceField, self).clean(value)
        if value is None or not isinstance(queryset, QuerySet):
            return queryset
        object_list = dict((
            (unicode(key), value)
            for key, value in queryset.in_bulk(value).iteritems()))
        return [object_list[unicode(pk)] for pk in value]
