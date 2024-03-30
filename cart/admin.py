from django.contrib import admin
from .models import Cart, CartStatus
# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'goods', 'number', 'is_checked']


@admin.register(CartStatus)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'battery_level', 'following_mode', 'charging', 'location', 'product_recognition_active']
