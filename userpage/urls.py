from django.urls import path
from .views import *

urlpatterns = [
    path('',index, name='home'),
    path('about',about, name='about'),
    path('contact',contact, name='contact'),
    path('products',products,name='products'),
    path('productdetails/<int:product_id>',productDetails,name='productdetails'),
    path('addtocart/<int:product_id>',addtocart, name='addtocart'),
    path('cart',cart,name='cart'),
    path('deletecart/<int:cart_id>',delete_cart,name='delete-cart'),
    path('orderitem/<int:cart_id>/<int:product_id>',orderItem,name='orderitem'),
    path('stripe_form',stripForm,name='stripe_form'),
    path('create-checkout-session/<int:order_id>/<int:cart_id>',create_checkout_session),
    path('success/',stripSuccess,name='success'),
    path('my-orders',myorders,name='my-orders'),
    path('support-message',support_message,name='support-message'),
]
