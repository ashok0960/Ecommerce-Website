from django.contrib import admin
from .models import *

# Register your models here.

class AdminCategory(admin.ModelAdmin):
    list_display = ['name','created_at']
    search_fields = ['name',]
    list_filter = ['created_at',]
admin.site.register(Category,AdminCategory)


class AdminProduct(admin.ModelAdmin):
    list_display = ['title','stock','discounted_price','trending','created_at']
    list_filter = ['created_at','trending','actual_price']
    search_fields = ['title','category','l_description']
admin.site.register(Product, AdminProduct)