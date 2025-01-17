from django.contrib import admin
from .models import User, Addr, Area, VerifCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'mobile', 'email', 'last_name']


@admin.register(Addr)
class AddrAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'name', 'province', 'city', 'county', 'address']


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['pid', 'name', 'level']


@admin.register(VerifCode)
class VerifCodeAdmin(admin.ModelAdmin):
    list_display = ['mobile', 'code', 'creat_time']
