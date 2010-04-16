# -*- coding: utf-8 -*-
from django.contrib import admin
from example.testapp.models import Car, ParkingArea


class ParkingAreaAdmin(admin.ModelAdmin):
    raw_id_fields = ('cars',)
    fieldsets = (
        ('bla', {
            'classes': ('wide',),
            'fields': (
                'name',
                'cars',
            ),
        }),
    )


admin.site.register(Car)
admin.site.register(ParkingArea, ParkingAreaAdmin)
