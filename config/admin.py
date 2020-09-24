from django.conf.urls import url
from django.contrib import admin, messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import ugettext as _


class CustomAdminSite(admin.AdminSite):
    site_header = _('Project Connect')
    site_title = _('Project Connect')
    index_title = _('Welcome to Project Connect')
    index_templates = 'admin/index.html'

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(r'^clear-cache/$', self.admin_view(self.clear_cache), name='admin_clear_cache'),
        ]
        return urls

    def clear_cache(self, request):
        cache.clear()
        messages.success(request, 'The cache has been cleared successfully.')
        return redirect('admin:index')
