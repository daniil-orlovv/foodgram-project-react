from rest_framework import permissions


class UpdateIfAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("PATCH", "DELETE"):
            return obj.author == request.user
        else:
            return True


class CreateIfAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated
        else:
            return True
