from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from proco.custom_auth.models import ApplicationUser


class ApplicationUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets
    fieldsets[2][1]['fields'] = ('is_active', 'is_confirmed', 'is_staff',
                                 'is_superuser', 'groups', 'user_permissions')


if not ApplicationUser._meta.abstract:
    admin.site.register(ApplicationUser, ApplicationUserAdmin)
