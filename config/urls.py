from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('locations/', include('proco.locations.api_urls')),
        path('locations/', include('proco.schools.api_urls')),
        path('statistics/', include('proco.connection_statistics.api_urls')),
        path('contact/', include('proco.contact.api_urls')),
    ])),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
