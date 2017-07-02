from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            if view.action in ('upvote', 'downvote'):
                return True
            return obj.author == request.user or request.user.is_staff


class CreateAndViewPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            if view.action == 'create':
                return request.user.is_authenticated()
            if view.action == 'update' or view.action == 'partial_update':
                return False
            return request.user.is_staff
