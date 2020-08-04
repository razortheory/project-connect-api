from rest_framework import permissions


class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user
        )


class IsSelfOrReadOnly(IsSelf):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or super(IsSelfOrReadOnly, self).has_object_permission(request, view, obj)
        )


class IsNewOrIsAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return (
            request.method == 'POST'
            or super(IsNewOrIsAuthenticated, self).has_permission(request, view)
        )


class ObjIsAuthenticated(permissions.BasePermission):
    """
    This permission needed for disable `/users/me/` endpoint for AnonymousUser.
    Unlike IsAuthenticated permission it doesn't disable another functions of viewset.
    """
    def has_object_permission(self, request, view, obj):
        return obj.is_authenticated()
