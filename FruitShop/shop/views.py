"""
Views for shop app.
"""

from django.shortcuts import render, redirect
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import HttpResponseRedirect

from shop.models import Category, Product , Cart

class HomeView(LoginRequiredMixin, View):
    """
    Home page view.
    """
    def get(self, request):
        return render(request, 'index.html')


class ShopView(LoginRequiredMixin, View):
    """
    Shop items view.
    """
    def get(self, request):
        all_products = Product.objects.all().order_by('?')
        context = {
            'all_products': all_products
        }

        return render(request, 'shop.html', context)


class SingleProductView(LoginRequiredMixin, View):
    """
    Single product view.
    """
    def get(self, request, product_slug):
        random_products = Product.objects.all().order_by('?')
        products = Product.objects.get(slug=product_slug)

        context = {
            'random_products': random_products,
            'products': products
        }

        return render(request, 'single-product.html', context)


class AddToCart(LoginRequiredMixin, View):
    """
    Products add into cart view.
    """
    def post(self, request, product_id):
        auth_user = request.user       
        product = Product.objects.get(id=product_id)
        Cart(user=auth_user,product=product).save()

        return redirect('index')


class CartVIew(LoginRequiredMixin, View):
    """
    Cart page view.
    """
    def get(self, request):
        auth_user = request.user
        cart_items = Cart.objects.filter(user=auth_user)

        carts = Cart.objects.all()
        cart = carts.filter(user=self.request.user).order_by('-id').distinct()

        amount = 0
        shipping = 45
        for i in cart:
            value = i.quantity * i.product.price
            amount = amount + value
        total = amount + shipping

        context = {
            'cart_items': cart_items,
            'shipping_amount': shipping,
            'cart_amount': amount,
            'total_amount': total
        }
        return render(request, 'cart.html', context)


class CheckoutView(LoginRequiredMixin, View):
    """
    Checkout page view.
    """
    def get(self, request):
        carts = Cart.objects.all()
        cart = carts.filter(user=self.request.user).order_by('-id').distinct()

        amount = 0
        shipping = 45
        for i in cart:
            value = i.quantity * i.product.price
            amount = amount + value
        total = amount + shipping

        context = {
            'total_amount': total,
            'shipping_amount': shipping,
            'carts': cart,
            'sub_total': amount,
        }
        return render(request, 'checkout.html', context)