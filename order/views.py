import datetime

from django.db import transaction
import time
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from cart.models import Cart
from common.pay import Pay
from users.models import Addr
from .models import OrderGoods, Order, Comment
from .serializer import OrderSerializer, OrderGoodsSerializer, CommentSerializer
from .permissions import OrderPermission


class OrderView(GenericViewSet,
                mixins.ListModelMixin
                ):
    queryset = Order.objects.all().order_by('-creat_time')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]
    # 指定商品过滤的字段
    filterset_fields = ['status']

    # 对整个视图的操作开启事务
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """提交订单视图"""
        # 获取请求参数
        addr = request.data.get('addr')
        # 判断收货地址是否存在
        if not Addr.objects.filter(id=addr, user=request.user).exists():
            return Response({'error': "传入的收货地址有误！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        aobj = Addr.objects.get(id=addr)
        addr_str = '{}{}{}{}  {}  {}'.format(aobj.province, aobj.city, aobj.county, aobj.address, aobj.name, aobj.phone)
        # 获取购物车中选中的商品
        cart_goods = Cart.objects.filter(user=request.user, is_checked=True)
        if not cart_goods.exists():
            return Response({'error': "订单提交失败，未选中商品"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 生成一个订单编号
        order_code = str(int(time.time())) + str(request.user.id)

        # 设置事务保存点
        save_id = transaction.savepoint()

        try:
            # 创建订单
            order = Order.objects.create(user=request.user, addr=addr_str, order_code=order_code, amount=0)
            # 保存商品总价
            amount = 0
            for cart in cart_goods:
                # 获取购买商品的数量
                num = cart.number
                # 获取购买商品的价格
                price = cart.goods.price
                # 将价格进行累加
                amount += price * num
                # 判断商品购买数量是否大于商品库存
                if cart.goods.stock > num:
                    # 修改商品的库存和销量并且保存
                    cart.goods.stock -= num
                    cart.goods.sales += num
                    cart.goods.save()
                else:
                    transaction.savepoint_rollback(save_id)
                    return Response({'error': "创建失败，商品‘{}’库存不足".format(cart.goods.title)},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                # 在订单商品表中新增一条数据
                OrderGoods.objects.create(order=order, goods=cart.goods, price=price, number=num)
                # 删除购物车中该商品记录
                cart.delete()
            # 修改订单的金额
            order.amount = amount
            order.save()
        except Exception as e:
            # 事务回滚
            transaction.savepoint_rollback(save_id)
            return Response({'error': "服务处理异常，订单创建失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 提交事务保存数据到数据库
            transaction.savepoint_commit(save_id)
            ser = self.get_serializer(order)
            return Response(ser.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """获取订单列表"""

        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取订单的详情"""
        # 获取订单对象
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # 获取订单中的商品信息
        goods = OrderGoods.objects.filter(order=instance)
        # 对订单中的商品信息进行序列化
        order_goods = OrderGoodsSerializer(goods, many=True)
        # 将订单中的商品信息一起返回
        result = serializer.data
        result['goods_list'] = order_goods.data
        return Response(result)

    def close_order(self, request, *args, **kwargs):
        """关闭订单"""
        # 获取到订单的对象
        obj = self.get_object()
        # 校验订单是否处于未支付的状态
        if obj.status != 1:
            return Response({'error': "只能取消未支付订单"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 将订单状态改为关闭
        obj.status = 6
        # 保存
        obj.save()
        # 返回结果
        return Response({'message': "订单已关闭"})


class CommentView(GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin
                  ):
    """商品评价的接口"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    # 配置查询评价信息的过滤参数
    filterser_fields = ['goods', 'order']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """商品评价的接口"""
        # 获取参数
        order = request.data.get('order')
        # 校验订单编号是否为空
        if not order:
            return Response({'error': "订单id不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 订单是否存在，并且订单处于‘待评价’的状态
        if not Order.objects.filter(id=order).exists():
            return Response({'error': "订单ID有误！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        order_obj = Order.objects.get(id=order)
        if order_obj.user != request.user:
            return Response({'error': "没有评论该订单的权限！"}, status=status.HTTP_403_FORBIDDEN)
        if order_obj.status != 4:
            return Response({'error': "订单不处于待评价状态"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 获取订单评论详情参数
        comment = request.data.get('comment')
        if not isinstance(comment, list):
            return Response({'error': "订单评论参数comment格式有误！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 设置一个事务保存的节点
        save_id = transaction.savepoint()
        try:
            for item in comment:
                # 遍历参数中的商品评论信息
                # 校验参数是否有误
                if not isinstance(item, dict):
                    return Response({'error': "订单评论参数comment格式有误！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                # 获取当前这条评论信息
                goods = item.get('goods', None)
                if not OrderGoods.objects.filter(order=order_obj, goods__id=goods).exists():
                    return Response({'error': "订单中没有id为{}的商品".format(goods)},
                                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                # 往item中添加订单id和用户id
                item['user'] = request.user.id
                item['goods'] = goods

                # 添加一条评论记录
                ser = CommentSerializer(data=item)
                ser.is_valid()
                ser.save()

            # 修改订单的状态为已完成
            order.status = 5
            order.save()
        except Exception as e:
            # 事务回滚
            transaction.savepoint_rollback(save_id)
            return Response({'message': "评论失败"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        else:
            # 提交事务
            transaction.savepoint_commit(save_id)
            return Response({'message': "评论成功"}, status=status.HTTP_201_CREATED)


class OrderPayView(GenericViewSet):
    """订单支付接口"""
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """支付"""
        order_id = request.data.get('orderID')
        if not Order.objects.filter(id=order_id, user=request.user).exists():
            return Response('订单编号有误！', status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 查询当前订单
        order = Order.objects.get(id=order_id)
        # 获取订单的总金额
        amount = order.amount
        # 获取订单的编号
        order_on = order.order_code
        # 生成支付宝支付的页面地址
        pay_url = Pay().mobile_pay_url(order_on, amount)

        return Response({'pay_url': pay_url, 'message': "OK"}, status=status.HTTP_200_OK)

    def get_pay_result(self, request):
        """获取支付结果"""
        # 获取参数
        order_code = request.query_params.get('order_code')
        if not Order.objects.filter(order_code=order_code).exists():
            return Response({"message": "订单编号有误！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        order = Order.objects.get(order_code=order_code)
        if order.status != 1:
            return Response({"message": "该订单不处于支付"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 调用支付宝的接口查询订单支付结果
        result = Pay().get_pay_result(order.order_code)
        if result['trade_status'] == 'TRADE_SUCCESS':
            # 修改支付的状态
            order.status = 2
            order.pay_type = 1
            order.pay_time = datetime.datetime.now()
            order.trade_no = result['trade_no']
            # 保存
            order.save()
        return Response(result, status=status.HTTP_200_OK)

    def alipay_callback_result(self):
        """支付宝支付成功之后的回调接口（给支付宝调用的）"""

        # 获取支付宝传递过来的回调参数

        # 解析数据并校验身份

        # 修改订单的支付状态
        return Response(status=status.HTTP_200_OK)
