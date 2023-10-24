from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    '''Пермишенс для авторов рецепта.'''
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class AdminOrReadOnly(permissions.BasePermission):
    '''Пермишенс для администратора для доступа к тегам и ингредиентам.'''
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )
