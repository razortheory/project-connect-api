from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', include('proco.custom_auth.urls')),
    path('api/', include([
        path('fcm/', include('proco.fcm.api_urls')),
        path('custom-auth/', include('proco.custom_auth.api_urls')),
    ])),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
