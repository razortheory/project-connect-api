from django.conf.urls import url
from django.contrib import admin, messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from proco.utils.cache import cache_manager


class CustomAdminSite(admin.AdminSite):
    site_header = _('Project Connect')
    site_title = _('Project Connect')
    index_title = _('Welcome to Project Connect')
    index_templates = 'admin/index.html'

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^clear-cache/$', self.admin_view(self.clear_cache), name='admin_clear_cache'),
            url(r'^invalidate-cache/$', self.admin_view(self.invalidate_cache), name='admin_invalidate_cache'),
        ]
        return urls

    def clear_cache(self, request):
        cache.clear()

        messages.success(request, 'The cache has been cleared successfully.')
        return redirect('admin:index')

    def invalidate_cache(self, request):
        cache_manager.invalidate()

        messages.success(request, 'The cache has been invalidated successfully.')
        return redirect('admin:index')
