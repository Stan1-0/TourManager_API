from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Allow read-only access to anyone; write access only to admin users."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and getattr(request.user, 'is_admin', False))


class IsOwnerOrAdmin(BasePermission):
    """Allow object owners to edit/view and admins to do anything."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to authenticated users (or can be further restricted by view)
        if request.method in SAFE_METHODS:
            return True

        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False

        # If object has `user` attribute (Booking, Review, Favorite)
        owner = getattr(obj, 'user', None)
        if owner is not None:
            return owner == user or getattr(user, 'is_admin', False) or getattr(user, 'is_superuser', False)

        # If object is a User instance
        if hasattr(obj, 'email') and hasattr(user, 'email'):
            return obj == user or getattr(user, 'is_admin', False) or getattr(user, 'is_superuser', False)

        # Fallback deny
        return False
