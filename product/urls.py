from django.urls import path
from .views import *

urlpatterns = [

    # Dashboards
    path('dashboard', adminDashboard, name='admin-dashboard'),
    path('vendor-dashboard', vendorDashboard, name='vendor-dashboard'),

    # Category
    path('add-category',addCategory,name='add-category'),
    path('all-category',allCategory,name='all-category'),
    path('delete-category/<int:category_id>',deleteCategory,name='delete-category'),
    path('update-category/<int:category_id>',updateCategory,name='update-category'),

    # Products
    path('add-product',addProduct,name='add-product'),
    path('all-products',allProducts,name='all-products'),
    path('delete-product/<int:product_id>',deleteProduct,name='delete-product'),
    path('update-product/<int:product_id>',updateProduct,name='update-product'),

    # Order Management
    path('manage-orders', manage_orders, name='manage-orders'),
    path('update-order-status/<int:order_id>', update_order_status, name='update-order-status'),
]

