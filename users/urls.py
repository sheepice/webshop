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

from django.urls import path
from users import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # 登录
    path('login/', views.LoginView.as_view()),
    # 注册
    path('register/', views.RegisterView.as_view()),
    # 刷新token
    path('token/refresh/', TokenRefreshView.as_view()),
    # 校验token
    path('token/verify/', TokenVerifyView.as_view()),
    # 获取单个用户信息的路由
    path('users/<int:pk>/', views.UserView.as_view({'get': 'retrieve'})),
    # 上传用户头像接口
    path('<int:pk>/avatar/upload', views.UserView.as_view({"post": "upload_avatar"})),
    # 添加地址和获取地址的路由
    path('address/', views.AddrView.as_view({"post": "create", "get": "list"})),
    # 修改收货地址和删除收货地址
    path('address/<int:pk>/', views.AddrView.as_view({"delete": "destroy", "put": "update"})),
    # 设置默认收货地址
    path('address/<int:pk>/default', views.AddrView.as_view({"put": "set_default_addr"})),
    # 发送短信验证码的接口
    path('sendsms/', views.SendMSView.as_view()),
    # 绑定手机号
    path('<int:pk>/mobile/bind', views.UserView.as_view({"put": "bind_mobile"})),
    # 解绑手机号
    path('<int:pk>/mobile/unbind', views.UserView.as_view({"put": "unbind_mobile"})),
    # 修改用户昵称
    path('<int:pk>/name/', views.UserView.as_view({"put": "update_name"})),
    # 修改用户邮箱
    path('<int:pk>/email/', views.UserView.as_view({"put": "update_email"})),
    # 修改用户密码
    path('<int:pk>/password/', views.UserView.as_view({"put": "update_password"})),
    # 获取省市区县数据的路由
    path('area/', views.AreaView.as_view({"get": "list"})),

]
