from rest_framework.permissions import BasePermission, SAFE_METHODS

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        return request.user and request.user.is_staff

class IsCommentUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return obj.user == request.user or request.user.is_staff
