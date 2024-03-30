from rest_framework import serializers
from users.models import User, Addr, Area


class UserSerializer(serializers.ModelSerializer):
    """用户模型的序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'mobile', 'avatar', 'last_name']


class AddrSerializer(serializers.ModelSerializer):
    """收货地址模型序列化器"""
    class Meta:
        model = Addr
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    """地区数据模型序列化器"""
    class Meta:
        model = Area
        fields = '__all__'
