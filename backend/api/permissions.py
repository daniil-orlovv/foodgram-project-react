from rest_framework import permissions


class UpdateIfAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('PATCH', 'DELETE'):
            return obj.author == request.user
        return True


class CreateIfAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True


class AuthUserDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user.is_authenticated
        return True


class RecipePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method == 'GET':
            return not user.is_authenticated
        elif request.method in ['GET', 'POST']:
            return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in ['PUT', 'DELETE']:
            return obj.author == user
