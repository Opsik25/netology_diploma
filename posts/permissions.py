from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Проверка прав владельца объекта."""

        return request.user == obj.user or request.user.is_staff
