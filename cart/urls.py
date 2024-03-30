from django.urls import path
from . import views

urlpatterns = [
    # 添加商品到购物车和获取购物车商品列表
    path('goods/', views.CartView.as_view({'post': 'create', 'get': 'list'})),
    # 修改商品的选中状态
    path('goods/<int:pk>/checked/', views.CartView.as_view({'put': "update_goods_status"})),
    # 修改商品的数量
    path('goods/<int:pk>/number/', views.CartView.as_view({'put': "update_goods_number"})),
    # 删除购物车中的商品
    path('goods/<int:pk>/', views.CartView.as_view({'delete': "destroy"})),
]
