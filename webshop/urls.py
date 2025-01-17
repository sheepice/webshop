"""
URL configuration for webshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
# 获取文件的视图
from users.views import FileView

urlpatterns = [
    path('admin/', admin.site.urls),
    # 获取图片资源的接口
    re_path(r'file/image/(.+?)/', FileView.as_view()),
    # 用户模块接口
    path('api/users/', include('users.urls')),
    # 商品模块接口
    path('api/goods/', include('goods.urls')),
    # 购物车模块接口
    path('api/cart/', include('cart.urls')),
    # 订单模块接口
    path('api/order/', include('order.urls')),
]
