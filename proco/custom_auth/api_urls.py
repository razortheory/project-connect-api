from django.urls import include, path

from rest_framework import routers

from proco.custom_auth import api

router = routers.SimpleRouter()
router.register('users', api.UserViewSet, basename='users')
router.register('auth', api.UserAuthViewSet, basename='auth')


app_name = 'custom-auth-api'
urlpatterns = [
    path('', include(router.urls)),
]
