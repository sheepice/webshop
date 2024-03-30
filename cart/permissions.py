from rest_framework import permissions


class CartPermission(permissions.BasePermission):
    """购物车对象操作权限"""

    def has_object_permission(self, request, view, obj):
        # 判断操作的用户对象和登陆的用户对象是否为同一个用户
        return obj.user == request.user
