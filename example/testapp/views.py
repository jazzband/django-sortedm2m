from django.views.generic import UpdateView

from .models import ParkingArea


class ParkingAreaUpdate(UpdateView):
    model = ParkingArea


parkingarea_update = ParkingAreaUpdate.as_view()
