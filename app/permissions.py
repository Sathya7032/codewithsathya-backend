from rest_framework import permissions

class AdminCreatedOnly(permissions.BasePermission):
    """
    Only allow admin-created users (superusers or staff) to create, update, or delete.
    All users can perform read-only (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow POST/PUT/DELETE only for admin-created users
        return request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)
