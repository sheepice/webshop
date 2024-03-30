from django.urls import path
from . import views
# 订单模块的api路由配置
urlpatterns = [
    # 提交订单的接口
    path('submit/', views.OrderView.as_view({'post': "create"})),
    # 获取订单列表的接口
    path('order/', views.OrderView.as_view({'get': "list"})),
    # 获取单个订单的详情数据和取消订单
    path('order/<int:pk>/', views.OrderView.as_view({'get': "retrieve", 'put': "close_order"})),
    # 商品评价的接口
    path('comment/', views.CommentView.as_view({'post': "create", 'get': "list"})),
    # 订单支付页面地址获取
    path('alipay/', views.OrderPayView.as_view({'post': "create", 'get': "get_pay_result"})),
    # 支付宝回调接口
    path('alipay/callback/', views.OrderPayView.as_view({'post': "alipay_callback_result"})),

]
