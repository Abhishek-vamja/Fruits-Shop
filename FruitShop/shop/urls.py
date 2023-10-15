"""
Urls for shop.
"""
from django.urls import path
from shop.views import *

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),

    path('items/', ShopView.as_view(), name='shop'),
    path('items/<slug:product_slug>/', SingleProductView.as_view(), name='single_product'),
    
    path('cart/', CartVIew.as_view(), name='cart'),
    path('update_quantity/<str:cart_id>/', CartVIew.update_quantity, name='update_quantity'),
    path('remove_quantity/<str:cart_id>/', CartVIew.remove_quantity, name='remove_quantity'),
    path('remove_from_cart/<str:cart_id>/', CartVIew.remove_from_cart, name='remove_from_cart'),
    path('add_to_cart/<slug:product_slug>/', AddToCart.as_view(), name='add_to_cart'),

    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('order/', OrderView.as_view(), name='order'),
    path('delete_order/<str:product_id>/', OrderView.delete_order, name='delete_order')
]