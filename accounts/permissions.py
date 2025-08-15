# from rest_framework.permissions import BasePermission
# from rest_framework import permissions
#
#
# class IsTourist(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.role == 'tourist'
#
#
# class IsOrganizer(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.role == 'organizer'
#
#
# class IsAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.role == 'admin'
#
#
# class IsGuide(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.role == 'guide'

from rest_framework.permissions import BasePermission

class IsTourist(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'tourist')


class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'organizer')


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsGuide(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'guide')
