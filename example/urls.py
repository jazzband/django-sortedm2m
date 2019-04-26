# -*- coding: utf-8 -*-
import django
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
import django.views.static

import example.testapp.views

admin.autodiscover()

if django.VERSION < (2, 2):
    def handle404(request):
        return HttpResponse('404')
else:
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
