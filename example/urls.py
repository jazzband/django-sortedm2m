# -*- coding: utf-8 -*-
import os
from django.conf.urls.defaults import *
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


SORTED_M2M_MEDIA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'src', 'sortedm2m', 'media', 'sortedm2m')


urlpatterns = patterns('',
    url(r'^media/sortedm2m/(.*)$', 'django.views.static.serve',
        {'document_root': SORTED_M2M_MEDIA}),
    url(r'^media/(.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls), name="admin"),
    url(r'^', include('staticfiles.urls')),
)
