from django.contrib import admin
from .models import *

class AdminSetting(admin.ModelAdmin):
    list_display = ['name','email','phone']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity','total_price','payment_method','payment_status','order_status','created_at']
    list_filter = ['order_status','payment_status','payment_method']
    search_fields = ['user__username','product__title']

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name','email','subject','created_at']
    search_fields = ['name','email','subject']

admin.site.register(Setting, AdminSetting)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
admin.site.register(Contact, ContactAdmin)

