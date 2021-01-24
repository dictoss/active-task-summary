from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

handler404 = 'ats.views.error404'
handler500 = 'ats.views.error500'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ats/', include('ats.urls')),
]
