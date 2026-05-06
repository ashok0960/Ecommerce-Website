from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('about', about, name='about'),
    path('contact', contact, name='contact'),
    path('products', products, name='products'),
    path('productdetails/<int:product_id>', productDetails, name='productdetails'),

    # Cart
    path('addtocart/<int:product_id>', addtocart, name='addtocart'),
    path('cart', cart, name='cart'),
    path('deletecart/<int:cart_id>', delete_cart, name='delete-cart'),

    # Orders
    path('orderitem/<int:cart_id>/<int:product_id>', orderItem, name='orderitem'),
    path('my-orders', myorders, name='my-orders'),

    # Stripe
    path('stripe_form', stripForm, name='stripe_form'),
    path('create-checkout-session/<int:order_id>/<int:cart_id>', create_checkout_session, name='create-checkout-session'),
    path('success/', stripSuccess, name='success'),

    # Wishlist
    path('wishlist', wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>', add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/<int:wishlist_id>', remove_from_wishlist, name='remove-from-wishlist'),

    # Profile
    path('profile', profile, name='profile'),

    # Chatbot & Support
    path('chatbot', chatbot, name='chatbot'),
    path('support-message', support_message, name='support-message'),
]
