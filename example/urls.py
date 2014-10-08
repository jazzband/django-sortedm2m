# -*- coding: utf-8 -*-
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse


admin.autodiscover()

def handle404(request):
    return HttpResponse('404')
def handle500(request):
    return HttpResponse('404')

handler404 = 'example.urls.handle404'
handler500 = 'example.urls.handle500'


urlpatterns = patterns('',
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls), name="admin"),
    url(r'^parkingarea/(?P<pk>\d+)/$', 'example.testapp.views.parkingarea_update', name='parkingarea'),
    url(r'^', include('django.contrib.staticfiles.urls')),
)
