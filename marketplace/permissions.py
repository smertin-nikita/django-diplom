from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return obj.user == request.user


class IsOwnerUser(BasePermission):
    """
    Object-level permission to allows access only to owners.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `user`.
        return obj.user == request.user


class OnlyEditToOrderStatus(BasePermission):
    """
    Object-level permission to allows only admins to edit status of order.
    """

    def has_object_permission(self, request, view, obj):
        # Todo Посмотреть откуда брать статус в
        # Instance must have an attribute named `status`.
        return obj.method == 'PATCH' and request.status

