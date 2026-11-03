from django.contrib import admin

from example.testapp.models import Car, Garage, ParkingArea


class ParkingAreaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('bla', {
            'classes': ('wide',),
            'fields': (
                'name',
                'cars',
            ),
        }),
    )


class ParkingAreaInlineAdmin(admin.StackedInline):
    model = ParkingArea
    extra = 0


class GarageAdmin(admin.ModelAdmin):
    inlines = [ParkingAreaInlineAdmin]


admin.site.register(Car)
admin.site.register(Garage, GarageAdmin)
admin.site.register(ParkingArea, ParkingAreaAdmin)
