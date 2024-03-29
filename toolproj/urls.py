from django.urls import include, path
from django.contrib import admin

admin.autodiscover()
admin.site.enable_nav_sidebar = False

handler404 = 'ats.views.error404'
handler500 = 'ats.views.error500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ats/', include('ats.urls')),
]
