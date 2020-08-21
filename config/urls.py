from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "Project Connect"
admin.site.site_title = "Project Connect"
admin.site.index_title = "Welcome to Project Connect"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('locations/', include('proco.locations.api_urls')),
        path('locations/', include('proco.schools.api_urls')),
    ])),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
