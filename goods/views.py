from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins, status
from goods.models import GoodsGroup, GoodsBanner, Goods, Collect, Detail
from goods.permissions import CollectPermission
from goods.serializers import GoodsSerializer, GoodsGroupSerializer, GoodsBannerSerializer, CollectSerializer, \
    DetailSerializer, CollectReadSerializer

"""
商品模块前台接口
1、商城首页：
    返回商品的分类信息
    返回商品的海报图
    返回商品列表（分页）
2、展示商品的详情信息 
3、分类获取商品列表
    支持分类获取（过滤参数：）
    获取推荐的商品
    根据商品销量排序、根据价格排序
4、收藏商品（取消）
"""


class IndexView(APIView):
    """商城首页数据获取的接口"""

    def get(self, request):
        # 获取商品所有的分类信息
        group = GoodsGroup.objects.filter(status=True)
        group_ser = GoodsGroupSerializer(group, many=True, context={'request': request})
        # 获取商品的海报图
        banner = GoodsBanner.objects.filter(status=True)
        banner_ser = GoodsBannerSerializer(banner, many=True, context={'request': request})
        # 获取所有的推荐商品
        goods = Goods.objects.filter(recommend=True)
        goods_ser = GoodsSerializer(goods, many=True, context={'request': request})
        result = dict(
            group=group_ser.data,
            banner=banner_ser.data,
            goods=goods_ser.data
        )

        return Response(result)


class GoodsView(ReadOnlyModelViewSet):
    """
    商品视图集：
        商品列表接口
        获取单个商品详情接口
    """
    queryset = Goods.objects.filter(is_on=True)
    serializer_class = GoodsSerializer
    # 实现通过商品分类和是否推荐进行过滤
    filterset_fields = ('group', 'recommend')
    # 实现通过价格和销量排序
    ordering_fields = ('sales', 'price', 'creat_time')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # 获取商品详情
        detail = Detail.objects.get(goods=instance)
        # 进行序列化
        detail_ser = DetailSerializer(detail)
        # 返回结果
        result = serializer.data
        result['detail'] = detail_ser.data
        return Response(result)


class CollectView(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    """
    delete:取消收藏
    list:收藏列表接口
    """
    queryset = Collect.objects.all()
    serializer_class = CollectSerializer
    # 设置认证用户才能有权访问
    permission_classes = [IsAuthenticated, CollectPermission]

    def create(self, request, *args, **kwargs):
        """收藏商品"""
        # 获取请求参数
        user = request.user
        params_user_id = request.data.get('user')
        # 校验请求参数中的用户id是否为当前登录的用户
        if user.id != params_user_id:
            return Response({'error': "没有操作其他用户的权限！"}, status=status.HTTP_403_FORBIDDEN)
        goods = request.data.get('goods')
        if not goods:
            return Response({'error': "参数goods不能为空！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            # 校验该商品是否已经收藏过了
        if self.queryset.filter(user=user, goods=goods).exists():
            return Response({'error': "不能重复收藏！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 调用继承过来的方法进行创建
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """获取用户的收藏列表"""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user)
        # 使用序列化器返回关联的商品字段数据
        serializer = CollectReadSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class GoodsGroupView(mixins.ListModelMixin,
                     GenericViewSet):

    """商品分类序列化器"""
    queryset = GoodsGroup.objects.filter(status=True)
    serializer_class = GoodsGroupSerializer
