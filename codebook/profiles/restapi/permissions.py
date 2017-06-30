from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated()
        else:
            if view.action == 'create':
                return (not request.user.is_authenticated()) or request.user.is_staff
            return request.user.is_authenticated() or view.action == 'list'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            if view.action == 'create' or view.action == 'list':
                return (not request.user.is_authenticated()) or request.user.is_staff
            elif view.action in ['follow', 'unfollow']:
                return obj.user_id != request.user.id
            return obj.user == request.user or request.user.is_staff
