from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser


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
    Object-level permission to allows access only to owners.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `user`.
        return obj.creator == request.user


class OnlyAdminEditToOrderStatus(BasePermission):
    """
    Object-level permission to allows only admins to edit status of order.
    """

    def has_object_permission(self, request, view, obj):
        # Todo Посмотреть откуда брать статус в
        # Instance must have an attribute named `status`.
        if bool(request.data.get('status')):
            return IsAdminUser.has_permission(self, request, view)
        return True

