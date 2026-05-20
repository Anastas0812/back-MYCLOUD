from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    #доступ только для пользователя с признаком is_admin

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )