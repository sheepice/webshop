from rest_framework import serializers

from goods.serializers import GoodsSerializer
from .models import Order, OrderGoods, Comment


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品详情序列化器"""
    goods = GoodsSerializer()

    class Meta:
        model = OrderGoods
        fields = ['goods', 'number', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """订单"""
    ordergoods_set = OrderGoodsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """订单评论"""
    user_name = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
