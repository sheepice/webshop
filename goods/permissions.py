from rest_framework import permissions


class CollectPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # 判断登录的账号是否是管理员
        if request.user.is_superuser:
            return True
        # 如果不是管理员，则判断操作的用户对象和登陆的用户对象是否为同一个用户
        return obj.user == request.user
