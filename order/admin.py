from django.contrib import admin
from .models import Order, OrderGoods, Comment
# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'addr', 'order_code', 'amount', 'status', 'pay_type', 'pay_time', 'trade_no']


@admin.register(OrderGoods)
class OrderGoodsAdmin(admin.ModelAdmin):
    list_display = ['order', 'goods', 'price', 'number']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['order', 'goods', 'user', 'content', 'rate', 'star']
