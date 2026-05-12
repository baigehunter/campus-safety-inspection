from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """仅管理员可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrSafetyManager(permissions.BasePermission):
    """管理员或安全管理员可访问"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'safety_manager']


class IsAdminOrSafetyManagerOrReadOnly(permissions.BasePermission):
    """管理员/安全管理员可写，其他认证用户只读"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'safety_manager']


class IsInspector(permissions.BasePermission):
    """巡检员可访问"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'inspector'


class IsRectifier(permissions.BasePermission):
    """整改负责人可访问"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'rectifier'


class IsOwnerOrAdmin(permissions.BasePermission):
    """用户本人或管理员可访问"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        # 检查对象是否有 user 字段
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # 检查对象是否有 inspector 字段
        if hasattr(obj, 'inspector'):
            return obj.inspector == request.user
        # 检查对象是否有 assignee 字段
        if hasattr(obj, 'assignee'):
            return obj.assignee == request.user
        return False


class CanAssignTask(permissions.BasePermission):
    """可派单：管理员或安全管理员"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'safety_manager']


class CanReviewTask(permissions.BasePermission):
    """可验收：管理员或安全管理员"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'safety_manager']


class CanSubmitRectify(permissions.BasePermission):
    """可提交整改：整改负责人本人"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'rectifier'

    def has_object_permission(self, request, view, obj):
        return obj.assignee == request.user


class CanCreateInspection(permissions.BasePermission):
    """可创建巡检记录：巡检员"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'inspector'


class CanCreateHazard(permissions.BasePermission):
    """可上报隐患：巡检员"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'inspector'


class CanResetPassword(permissions.BasePermission):
    """可重置密码：仅管理员"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'


class CanDeleteUser(permissions.BasePermission):
    """可删除用户：仅超级管理员"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'
