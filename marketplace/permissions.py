from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser


class IsAdminUserOrReadOnly(IsAdminUser):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `creator` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `creator`.
        return obj.creator == request.user


class IsOwnerUser(BasePermission):
    """
    Object-level permission to allows access to object only to owners.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `user`.
        return obj.creator == request.user


class IsOwnerOrAdminUser(BasePermission):
    """
    Object-level permission to allows access to object only to owners or admins.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `creator`.
        return obj.creator == request.user or request.user.is_staff





