# # tours/permissions.py
# from rest_framework import permissions
#
#
# class IsAdminOrOrganizerOwnerOrReadOnly(permissions.BasePermission):
#     """
#     Admins: full access.
#     Organizers: full access to their own tours and assignments.
#     Tourists/others: read-only.
#     """
#
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#
#         # Write permissions for authenticated admins or organizers
#         return request.user.is_authenticated and request.user.role in ['admin', 'organizer']
#
#     def has_object_permission(self, request, view, obj):
#         # Read only for everyone
#         if request.method in permissions.SAFE_METHODS:
#             return True
#
#         if request.user.role == 'admin':
#             return True
#
#         # Organizers can modify only their own tours or related objects
#         # For TourGuideAssignment, check the tour organizer ownership
#         if hasattr(obj, 'organizer'):
#             return obj.organizer == request.user
#         if hasattr(obj, 'tour'):
#             return obj.tour.organizer == request.user
#
#
# class IsGuideSelf(permissions.BasePermission):
#     """Allow only the guide assigned to respond."""
#
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_authenticated and obj.guide == request.user
#
#
# class IsOrganizerOrAdmin(permissions.BasePermission):
#     """Allow only organizers or admins to manage assignments (assign/cancel)."""
#
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role in ['organizer', 'admin']

# tours/permissions.py
from rest_framework import permissions

class IsAdminOrOrganizerOwnerOrReadOnly(permissions.BasePermission):
    """
    Admins: full access.
    Organizers: full access to their own tours (and related tour-owned objects).
    Tourists/others: read-only.
    """

    def has_permission(self, request, view):
        # Safe methods are allowed for everyone (list/retrieve).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for authenticated admins or organizers
        return bool(request.user and request.user.is_authenticated and request.user.role in ['admin', 'organizer'])

    def has_object_permission(self, request, view, obj):
        # Safe methods are allowed for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admins can do anything
        if request.user.role == 'admin':
            return True

        # Organizers can modify only their own tours or objects owned by their tour
        # obj may be a Tour or a related object with .tour or .organizer attribute
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        if hasattr(obj, 'tour'):
            return obj.tour.organizer == request.user

        # Otherwise deny
        return False


class IsGuideSelf(permissions.BasePermission):
    """Allow only the assigned guide user to respond to an assignment."""
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and obj.guide == request.user)


class IsOrganizerOrAdmin(permissions.BasePermission):
    """Allow only organizers or admins to manage assignments (assign/cancel)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['organizer', 'admin'])
