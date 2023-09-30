from rest_framework import permissions


class OnlyAuthorized(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated)
