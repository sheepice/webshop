from django.db import models
from common.db import BaseModel


class Cart(BaseModel):
    """购物车模型"""
    user = models.ForeignKey('users.User', help_text='用户ID', verbose_name='用户ID', on_delete=models.CASCADE, blank=True)
    goods = models.ForeignKey('goods.Goods', help_text='商品ID', verbose_name='商品ID', on_delete=models.CASCADE)
    number = models.SmallIntegerField(help_text='商品数量', verbose_name='商品数量', default=1, blank=True)
    is_checked = models.BooleanField(help_text='是否选中', verbose_name='是否选中', default=True, blank=True)

    class Meta:
        db_table = 'cart'
        verbose_name = '购物车'
        verbose_name_plural = verbose_name


class CartStatus(models.Model):
    cart_id = models.CharField(max_length=100, unique=True, help_text='购物车ID', verbose_name='购物车ID')
    battery_level = models.IntegerField(help_text='电池电量', verbose_name='电池电量')
    following_mode = models.BooleanField(help_text='运行模式', verbose_name='运行模式')
    charging = models.BooleanField(help_text='充电状态', verbose_name='充电状态')
    location = models.CharField(max_length=255, help_text='位置', verbose_name='位置')
    product_recognition_active = models.BooleanField(help_text='工作状态', verbose_name='工作状态')
    timestamp = models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')

    def __str__(self):
        return f"Cart {self.cart_id} Status"

    class Meta:
        db_table = 'cart_status'
        verbose_name = '购物车实时状态'
        verbose_name_plural = verbose_name
