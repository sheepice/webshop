"""
商品模块序列化器
"""
from .models import Goods, GoodsGroup, GoodsBanner, Detail, Collect
from rest_framework import serializers


class GoodsSerializer(serializers.ModelSerializer):
    """商品序列化器"""

    class Meta:
        model = Goods
        fields = "__all__"


class GoodsGroupSerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsGroup
        fields = "__all__"


class GoodsBannerSerializer(serializers.ModelSerializer):
    """商品海报序列化器"""

    class Meta:
        model = GoodsBanner
        fields = "__all__"


class DetailSerializer(serializers.ModelSerializer):
    """商品详情序列化器"""

    class Meta:
        model = Detail
        fields = ['producer', 'norms', 'details']


class CollectSerializer(serializers.ModelSerializer):
    """商品收藏序列化器"""

    class Meta:
        model = Collect
        fields = "__all__"


class CollectReadSerializer(serializers.ModelSerializer):
    """商品收藏序列化器"""
    # 返回关联的商品字段数据
    goods = GoodsSerializer()

    class Meta:
        model = Collect
        fields = "__all__"
