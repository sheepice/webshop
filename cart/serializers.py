from goods.serializers import GoodsSerializer
from .models import Cart, CartStatus
from rest_framework import serializers


class CartSerializer(serializers.ModelSerializer):
    """写入：购物车序列化器"""
    class Meta:
        model = Cart
        fields = "__all__"


class ReadCartSerializer(serializers.ModelSerializer):
    """读取：购物车信息序列化器"""
    goods = GoodsSerializer()

    class Meta:
        model = Cart
        fields = "__all__"


class CartStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartStatus
        fields = '__all__'
