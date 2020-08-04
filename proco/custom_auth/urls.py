from django.contrib.auth import views as auth_views
from django.urls import path

from proco.custom_auth.models import ApplicationUser
from proco.custom_auth.views import account_confirm

app_name = 'custom-auth'
urlpatterns = [
    path(
        'reset-password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='custom_auth/password_reset_form.html',
            token_generator=ApplicationUser.reset_password_token_generator,
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset-password/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='custom_auth/password_reset.html'),
        name='password_reset_complete',
    ),
    path(
        'confirm/<uidb64>/<token>/',
        account_confirm, {'token_generator': ApplicationUser.confirm_account_token_generator},
        name='account_confirm',
    ),
]
