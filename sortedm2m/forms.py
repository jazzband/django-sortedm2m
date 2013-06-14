# -*- coding: utf-8 -*-
from itertools import chain
from django import forms
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.template import Context, Template


STATIC_URL = getattr(settings, 'STATIC_URL', settings.MEDIA_URL)

class SortedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    class Media:
        js = (
            STATIC_URL + 'sortedm2m/widget.js',
            STATIC_URL + 'sortedm2m/jquery-ui.js',
        )
        css = {'screen': (
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

        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])

        selected = []
        unselected = []

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
            item = {'label_for': label_for, 'rendered_cb': rendered_cb, 'option_label': option_label}
            if option_value in str_values:
                selected.append(item)
            else:
                unselected.append(item)

        template = """{% spaceless %}
        <div class="selector-chosen sortedm2m-container">
        <h2>Choose items and order (drag)</h2>

        <ul>
        {% for row in selected %}
            <li><label {{ row.label_for }}>{{ row.rendered_cb }} {{ row.option_label }}</label></li>
        {% endfor %}

        {% for row in unselected %}
            <li><label {{ row.label_for }}>{{ row.rendered_cb }} {{ row.option_label }}</label></li>
        {% endfor %}
        </ul>

        <div style="clear: both;"></div>

        </div>
        {% endspaceless %}"""

        html = Template(template).render(Context({'selected': selected, 'unselected': unselected}))
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if isinstance(value, basestring):
            return [v for v in value.split(',') if v]
        return value


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
