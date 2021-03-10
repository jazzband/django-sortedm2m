import django.views.static
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, re_path

import example.testapp.views

admin.autodiscover()


def handle404(request, exception):
    return HttpResponse("404")


def handle500(request):
    return HttpResponse("500")


handler404 = "example.urls.handle404"
handler500 = "example.urls.handle500"


if django.VERSION < (1, 9):
    urlpatterns = [re_path(r"^admin/", include(admin.site.urls), name="admin")]
else:
    urlpatterns = [re_path(r"^admin/", admin.site.urls, name="admin")]

urlpatterns += [
    re_path(
        r"^media/(.*)$",
        django.views.static.serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
    re_path(
        r"^parkingarea/(?P<pk>\d+)/$",
        example.testapp.views.parkingarea_update,
        name="parkingarea",
    ),
    re_path(r"^", include("django.contrib.staticfiles.urls")),
]
