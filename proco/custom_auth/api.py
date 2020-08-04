from django.contrib.auth import get_user_model

from rest_framework import decorators, mixins, permissions, status, viewsets
from rest_framework.response import Response

from proco.custom_auth.permissions import IsNewOrIsAuthenticated, IsSelf
from proco.custom_auth.serializers import ResetPasswordByEmailSerializer, UsernameLoginSerializer, UserSerializer


class ResetPasswordViewMixin(object):
    reset_password_serializer_class = ResetPasswordByEmailSerializer

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
                       url_path='reset-password')
    def reset_password(self, request, **kwargs):
        serializer = self.get_reset_password_serializer()
        serializer.is_valid(raise_exception=True)
        serializer.send_reset_password_email()
        return Response()

    def get_reset_password_serializer(self, **kwargs):
        return self.reset_password_serializer_class(data=self.request.data, **kwargs)


class UserViewSet(ResetPasswordViewMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects
    permission_classes = [IsSelf, IsNewOrIsAuthenticated]

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.kwargs[lookup_url_kwarg] == 'me':
            obj = self.request.user
            self.check_object_permissions(self.request, obj)
            return obj

        return super(UserViewSet, self).get_object()


class UserAuthViewSet(viewsets.ViewSet):
    NEW_TOKEN_HEADER = 'X-Token'

    login_serializer_class = UsernameLoginSerializer

    @decorators.action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
                       url_path='login')
    def basic_login(self, request):
        serializer = self.get_login_serializer()
        serializer.is_valid(raise_exception=True)
        self.user = serializer.authenticate()
        return Response(status=status.HTTP_201_CREATED, headers=self.get_success_headers())

    def get_login_serializer(self, **kwargs):
        return self.login_serializer_class(data=self.request.data, **kwargs)

    def get_success_headers(self):
        return {self.NEW_TOKEN_HEADER: self.user.user_auth_tokens.create()}

    @decorators.action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated],
                       url_path='logout')
    def logout(self, request):
        auth_token = request._request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
        request.user.user_auth_tokens.filter(key=auth_token).delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
