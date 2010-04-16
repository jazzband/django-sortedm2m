# -*- coding: utf-8 -*-
from django import forms
from django.db.models.query import QuerySet


class SortedMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        queryset = super(SortedMultipleChoiceField, self).clean(value)
        if value is None or not isinstance(queryset, QuerySet):
            return queryset
        object_list = dict((
            (unicode(key), value)
            for key, value in queryset.in_bulk(value).iteritems()))
        return [object_list[unicode(pk)] for pk in value]
