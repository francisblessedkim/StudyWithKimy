from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "teacher"

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        # works for objects that have .author or .user or are the user itself
        owner = getattr(obj, "author", None) or getattr(obj, "user", None) or obj
        return owner == user
