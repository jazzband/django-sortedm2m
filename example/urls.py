import django.views.static
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse

import example.testapp.views

admin.autodiscover()


def handle404(request, exception):
    return HttpResponse('404')


def handle500(request):
    return HttpResponse('500')


handler404 = 'example.urls.handle404'
handler500 = 'example.urls.handle500'


if django.VERSION < (1, 9):
    urlpatterns = [url(r'^admin/', include(admin.site.urls), name="admin")]
else:
    urlpatterns = [url(r'^admin/', admin.site.urls, name="admin")]

urlpatterns += [
    url(r'^media/(.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^parkingarea/(?P<pk>\d+)/$', example.testapp.views.parkingarea_update, name='parkingarea'),
    url(r'^', include('django.contrib.staticfiles.urls')),
]
